function delForm(event) {
    event.preventDefault();
    event.currentTarget.parentElement.parentElement.remove();
    console.log(document.cookie);
}

function getForm() {
    const xhr = new XMLHttpRequest()
    xhr.open("GET", "./api/passform", false)
    xhr.send()
    return xhr.response
}

document.querySelector("#logout").addEventListener("click", event => {
    const xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "./?act=logout", false);
    xmlHttp.send();
})

document.querySelector(".add_password").addEventListener("click", event => {
    const passwords = document.querySelector(".passwords");
    if (passwords.querySelector(".passform") === null) {
        passwords.insertAdjacentHTML("beforeend", getForm());
    } else {
        return "";
    }
})

function getModal() {
    const xml = new XMLHttpRequest();
    xml.open("GET", "./api/modalpass", false);
    xml.send();
    return xml.response;
}

document.addEventListener("click", event => {
    const btn = event.target;
    if (btn.nodeName === "BUTTON" && btn.classList.contains("share")) {
        const login = btn.previousElementSibling.previousElementSibling.textContent;
        document.querySelector("body").insertAdjacentHTML("beforeend", getModal());
        document.querySelector(".modal").querySelector("input").value = login;
    }
})