const $ = id => document.getElementById(id);
let mode = "login";   // "login" or "register" (the same words as the server addresses)

function setMode(newMode) {
  mode = newMode;
  $("loginTab").classList.toggle("on", mode === "login");
  $("registerTab").classList.toggle("on", mode === "register");
  $("authButton").textContent = mode === "login" ? "Log in" : "Create account";
  $("authError").textContent = "";
}

$("loginTab").addEventListener("click", () => setMode("login"));
$("registerTab").addEventListener("click", () => setMode("register"));

$("authButton").addEventListener("click", async () => {
  try {
    const res = await fetch("/api/" + mode, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: $("username").value.trim(), password: $("password").value })
    });
    const data = await res.json();
    if (res.ok) {
      window.location.href = "/";
    } else {
      $("authError").textContent = data.error;
    }
  } catch (err) {
    $("authError").textContent = "Cannot reach the server.";
  }
});

setMode("login");
