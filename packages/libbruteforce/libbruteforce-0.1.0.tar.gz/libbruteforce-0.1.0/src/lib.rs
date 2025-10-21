use pyo3::exceptions::{PyRuntimeError, PyTypeError};
use pyo3::prelude::*;
use std::collections::BTreeSet;
use std::sync::mpsc::{self, TryRecvError};
use std::time::Duration;

#[pyclass]
struct AlphabetBuilder {
    chars: BTreeSet<char>,
}

impl AlphabetBuilder {}

#[pymethods]
impl AlphabetBuilder {
    #[new]
    fn new() -> Self {
        Self {
            chars: BTreeSet::new(),
        }
    }

    // Adds all digits 0-9 to the alphabet
    fn with_digits<'py>(mut slf: PyRefMut<'py, Self>) -> PyResult<PyRefMut<'py, Self>> {
        for c in '0'..='9' {
            slf.chars.insert(c);
        }
        Ok(slf)
    }

    // Adds all lowercase letters a-z to the alphabet
    fn with_lowercase<'py>(mut slf: PyRefMut<'py, Self>) -> PyResult<PyRefMut<'py, Self>> {
        for c in 'a'..='z' {
            slf.chars.insert(c);
        }
        Ok(slf)
    }

    // Adds all uppercase letters A-Z to the alphabet
    fn with_uppercase<'py>(mut slf: PyRefMut<'py, Self>) -> PyResult<PyRefMut<'py, Self>> {
        for c in 'A'..='Z' {
            slf.chars.insert(c);
        }
        Ok(slf)
    }

    // Adds symbols to the alphabet: !@#$%^&*()-_=+[]{}|;:',.<>/?`~\"
    fn with_symbols<'py>(mut slf: PyRefMut<'py, Self>) -> PyResult<PyRefMut<'py, Self>> {
        let symbols = "!@#$%^&*()-_=+[]{}|;:',.<>/?`~\\\"";
        for ch in symbols.chars() {
            slf.chars.insert(ch);
        }
        Ok(slf)
    }

    // Add custom characters to the alphabet
    fn with_custom<'py>(mut slf: PyRefMut<'py, Self>, s: &str) -> PyResult<PyRefMut<'py, Self>> {
        for ch in s.chars() {
            slf.chars.insert(ch);
        }
        Ok(slf)
    }

    // Remove previously added characters from the alphabet
    fn without_custom<'py>(mut slf: PyRefMut<'py, Self>, s: &str) -> PyResult<PyRefMut<'py, Self>> {
        for ch in s.chars() {
            slf.chars.remove(&ch);
        }
        Ok(slf)
    }

    // Convert the alphabet into a string
    fn build(&self) -> String {
        self.chars.iter().collect()
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("AlphabetBuilder(chars={:?})", self.build()))
    }
}

const ALG_IDENTITY: u8 = 0;
const ALG_MD5: u8 = 1;
const ALG_SHA1: u8 = 2;
const ALG_SHA256: u8 = 3;

#[pyclass]
struct BasicCrackParameter {
    alphabet: String,
    algo_id: u8,
    max_len: u32,
    min_len: u32,
    greedy: bool,
}

impl BasicCrackParameter {
    fn to_parameter(&self) -> libbruteforce_rs::BasicCrackParameter {
        let alphabet_box: Box<[char]> =
            self.alphabet.chars().collect::<Vec<_>>().into_boxed_slice();
        libbruteforce_rs::BasicCrackParameter::new(
            alphabet_box,
            self.max_len,
            self.min_len,
            self.greedy,
        )
    }
}

#[pymethods]
impl BasicCrackParameter {
    #[new]
    #[pyo3(signature = (alphabet, algo_id, min_len = 0, max_len = 32, greedy = true))]
    fn new(
        alphabet: &Bound<'_, PyAny>,
        algo_id: u8,
        min_len: u32,
        max_len: u32,
        greedy: bool,
    ) -> PyResult<Self> {
        // Accept either an AlphabetBuilder instance or a string.
        // If we receive an AlphabetBuilder instance, call its build() method.
        let alphabet_str = if let Ok(s) = alphabet.extract::<String>() {
            s
        } else if let Ok(builder_bound) = alphabet.cast::<AlphabetBuilder>() {
            let builder_ref = builder_bound.borrow();
            builder_ref.build()
        } else {
            return Err(PyTypeError::new_err(
                "Alphabet must be of type str or AlphabetBuilder",
            ));
        };

        // Validate that the algorithm selected is valid
        match algo_id {
            ALG_IDENTITY | ALG_MD5 | ALG_SHA1 | ALG_SHA256 => {}
            _ => {
                return Err(PyTypeError::new_err("The selected algorithm is unknown"));
            }
        }

        Ok(Self {
            alphabet: alphabet_str,
            algo_id,
            min_len,
            max_len,
            greedy,
        })
    }

    fn alphabet(&self) -> String {
        self.alphabet.clone()
    }

    fn max_len(&self) -> u32 {
        self.max_len
    }

    fn min_len(&self) -> u32 {
        self.min_len
    }

    fn greedy(&self) -> bool {
        self.greedy
    }

    fn algo_id(&self) -> u8 {
        self.algo_id
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!(
            "BasicCrackParameter(alphabet={:?}, algo_id={}, max_len={}, min_len={}, greedy={})",
            self.alphabet, self.algo_id, self.max_len, self.min_len, self.greedy
        ))
    }
}

#[pyclass]
struct Algorithm;

#[pymethods]
impl Algorithm {
    #[classattr]
    const IDENTITY: u8 = ALG_IDENTITY;

    #[classattr]
    const MD5: u8 = ALG_MD5;

    #[classattr]
    const SHA1: u8 = ALG_SHA1;

    #[classattr]
    const SHA256: u8 = ALG_SHA256;
}

#[pyfunction]
fn crack(
    py: Python<'_>,
    basic: PyRef<'_, BasicCrackParameter>,
    target_hash: &str,
) -> PyResult<Option<String>> {
    let algo_id = basic.algo_id;
    let basic_param = basic.to_parameter();
    let target_owned = target_hash.to_string();

    // Execute cracking on a dedicated thread.
    let (tx_res, rx_res) = mpsc::channel();
    let (tx_err, rx_err) = mpsc::channel();
    std::thread::spawn(move || {
        let work = || -> libbruteforce_rs::CrackResult {
            match algo_id {
                ALG_IDENTITY => {
                    let cp = libbruteforce_rs::CrackParameter::new(
                        basic_param,
                        libbruteforce_rs::hash_fncs::no_hashing(
                            libbruteforce_rs::TargetHashInput::HashAsStr(&target_owned),
                        ),
                    );
                    libbruteforce_rs::crack(cp)
                }
                ALG_MD5 => {
                    let cp = libbruteforce_rs::CrackParameter::new(
                        basic_param,
                        libbruteforce_rs::hash_fncs::md5_hashing(
                            libbruteforce_rs::TargetHashInput::HashAsStr(&target_owned),
                        ),
                    );
                    libbruteforce_rs::crack(cp)
                }
                ALG_SHA1 => {
                    let cp = libbruteforce_rs::CrackParameter::new(
                        basic_param,
                        libbruteforce_rs::hash_fncs::sha1_hashing(
                            libbruteforce_rs::TargetHashInput::HashAsStr(&target_owned),
                        ),
                    );
                    libbruteforce_rs::crack(cp)
                }
                ALG_SHA256 => {
                    let cp = libbruteforce_rs::CrackParameter::new(
                        basic_param,
                        libbruteforce_rs::hash_fncs::sha256_hashing(
                            libbruteforce_rs::TargetHashInput::HashAsStr(&target_owned),
                        ),
                    );
                    libbruteforce_rs::crack(cp)
                }
                _ => unreachable!("Unknown algorithm requested"),
            }
        };

        let caught = std::panic::catch_unwind(std::panic::AssertUnwindSafe(work));
        match caught {
            Ok(res) => {
                let _ = tx_res.send(res);
            }
            Err(payload) => {
                // Attempt to convert the panic into a string
                let msg = if let Some(s) = payload.downcast_ref::<&'static str>() {
                    s.to_string()
                } else if let Some(s) = payload.downcast_ref::<String>() {
                    s.clone()
                } else {
                    "kernel panicked".to_string()
                };
                let _ = tx_err.send(msg);
            }
        }
    });

    loop {
        // First, check if the worker reported a panic and turn it into a Python exception.
        match rx_err.try_recv() {
            Ok(panic_msg) => {
                return Err(PyRuntimeError::new_err(format!(
                    "Kernel panic: {}",
                    panic_msg
                )));
            }
            Err(TryRecvError::Empty) => {}
            Err(TryRecvError::Disconnected) => {}
        }

        match rx_res.try_recv() {
            Ok(result) => {
                let solution_opt = result.solution();
                return Ok(solution_opt.as_ref().map(|s| s.to_string()));
            }
            Err(TryRecvError::Empty) => {
                py.detach(|| std::thread::sleep(Duration::from_millis(50)));
                py.check_signals()?;
            }
            Err(TryRecvError::Disconnected) => {
                // This likely indicates that the cracking was
                // completed, but we failed to identify the solution.
                return Ok(None);
            }
        }
    }
}

#[pymodule]
fn libbruteforce(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<AlphabetBuilder>()?;
    m.add_class::<BasicCrackParameter>()?;
    m.add_class::<Algorithm>()?;
    m.add_function(wrap_pyfunction!(crack, m)?)?;
    Ok(())
}
