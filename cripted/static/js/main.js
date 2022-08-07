function delForm(event) {
    event.preventDefault();
    document.querySelector(".modal").remove();
    // console.log(document.cookie);
    document.cookie = "";
}

function getModal(url) {
    const xml = new XMLHttpRequest();
    xml.open("GET", url, false);
    xml.send();
    return xml.response;
}

document.querySelector("#logout").addEventListener("click", event => {
    const xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "./?act=logout", false);
    xmlHttp.send();
})

document.querySelector(".add_password").addEventListener("click", event => {
    const passwords = document.querySelector(".passwords");
    if (passwords.querySelector(".passform") === null) {
        passwords.insertAdjacentHTML("beforeend", getModal("./api/pass.add"));
    } else {
        return "";
    }
})

function shareBtn(event) {
    const btn = event.currentTarget;
    const login = btn.parentElement.previousElementSibling.querySelector(".datum").textContent;
    document.querySelector("body").insertAdjacentHTML("beforeend", getModal("./api/pass.share"));
    document.querySelector(".modal").querySelector("input").value = login;
}

function deletePass(event) {
    const btn = event.currentTarget;
    const login = btn.parentElement.previousElementSibling.querySelector(".datum").textContent;
    document.querySelector("body").insertAdjacentHTML("beforeend", getModal("./api/pass.delete"));
    document.querySelector(".modal").querySelector("input").value = login;
}

function viewToggle(event) {
    password = event.currentTarget.parentElement.previousElementSibling.querySelector(".secret_password");
    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    };
}
