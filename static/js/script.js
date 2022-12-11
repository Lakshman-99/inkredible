const checkbox = document.querySelector("input");
checkbox.checked = false;
const nav = document.getElementById("nav");
const toggleIcon = document.getElementById("toggle-icon");
const image1 = document.getElementById("image1");
const image2 = document.getElementById("image2");
const image3 = document.getElementById("image3");
const textBox = document.getElementById("text-box");

function imageMode(color) {
    image1.src = `static/img/undraw_proud_coder_${color}.svg`;
    image2.src = `static/img/undraw_feeling_proud_${color}.svg`;
    image3.src = `static/img/undraw_conceptual_idea_${color}.svg`;
}

function themeMode(color) {
    nav.style.backgroundColor =
        color == "dark" ? "rgb(0 0 0 / 50%)" : "rgb(255 255 255/ 50%)";
    textBox.style.backgroundColor =
        color == "dark" ? "rgb(255 255 255 / 50%)" : "rgb(0 0 0 / 50%)";
    toggleIcon.children[0].textContent =
        color == "dark" ? "Dark Mode" : "Light Mode";
    toggleIcon.children[1].classList.replace(
        `${color == "dark" ? "fa-sun" : "fa-moon"}`,
        color == "light" ? "fa-sun" : "fa-moon"
    );
    imageMode(color);
}

function onSwitch(event) {
    event.preventDefault();
    if (event.target.checked) {
        document.documentElement.setAttribute("data-theme", "dark");
        localStorage.setItem("theme", "dark");
        themeMode("dark");
    } else {
        document.documentElement.setAttribute("data-theme", "light");
        localStorage.setItem("theme", "light");
        themeMode("light");
    }
}

// Event listener
document
    .querySelector('input[type="checkbox"]')
    .addEventListener("change", onSwitch);

//localStorage check
const currTheme = localStorage.getItem("theme");
if (currTheme) {
    document.documentElement.setAttribute("data-theme", currTheme);
    currTheme == 'dark' ? checkbox.checked = true : checkbox.checked = false;
    themeMode(currTheme);
}
