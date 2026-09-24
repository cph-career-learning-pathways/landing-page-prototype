const sidebar = document.getElementById("sidebar");
const sidebarOpenButton = document.getElementById("sidebar-open");
const sidebarCloseButton = document.getElementById("sidebar-close");


function openSidebar() {
    sidebar.classList.add("is-open");
    sidebar.setAttribute("aria-hidden", "false");
}


function closeSidebar() {
    sidebar.classList.remove("is-open");
    sidebar.setAttribute("aria-hidden", "true");
}


sidebarOpenButton.addEventListener("click", openSidebar);

sidebarCloseButton.addEventListener("click", closeSidebar);