const AUTH_URL = "http://127.0.0.1:8000/auth";
const STORAGE_KEY = "x-api-key";

const loginView = document.getElementById("login-view");
const helloView = document.getElementById("hello-view");
const loginForm = document.getElementById("login-form");
const keyInput = document.getElementById("key-input");
const loginError = document.getElementById("login-error");
const logoutBtn = document.getElementById("logout-btn");

function authHeaders() {
  const key = localStorage.getItem(STORAGE_KEY);
  return key ? { [STORAGE_KEY]: key } : {};
}

// Wrapper for all app requests after login: always attaches the stored
// x-api-key header, read fresh from localStorage on every call.
function apiFetch(url, options = {}) {
  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...authHeaders(),
    },
  });
}
window.apiFetch = apiFetch;

function showLogin(message) {
  loginView.hidden = false;
  helloView.hidden = true;
  if (message) {
    loginError.textContent = message;
    loginError.hidden = false;
  } else {
    loginError.hidden = true;
  }
}

function showHello() {
  loginView.hidden = true;
  helloView.hidden = false;
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const key = keyInput.value.trim();
  if (!key) return;

  const submitBtn = loginForm.querySelector("button[type=submit]");
  submitBtn.disabled = true;
  loginError.hidden = true;

  try {
    const response = await fetch(AUTH_URL, {
      method: "POST",
      headers: { [STORAGE_KEY]: key },
    });

    if (response.status === 200) {
      localStorage.setItem(STORAGE_KEY, key);
      keyInput.value = "";
      showHello();
    } else {
      showLogin(`Authentication failed (status ${response.status}).`);
    }
  } catch (err) {
    showLogin("Could not reach the authentication server.");
  } finally {
    submitBtn.disabled = false;
  }
});

logoutBtn.addEventListener("click", () => {
  localStorage.removeItem(STORAGE_KEY);
  showLogin();
});

if (localStorage.getItem(STORAGE_KEY)) {
  showHello();
} else {
  showLogin();
}
