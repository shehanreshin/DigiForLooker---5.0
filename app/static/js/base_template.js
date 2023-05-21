let arrow = document.querySelectorAll(".arrow");
for (var i = 0; i < arrow.length; i++) {
  arrow[i].addEventListener("click", (e)=>{
 let arrowParent = e.target.parentElement.parentElement;//selecting main parent of arrow
 arrowParent.classList.toggle("showMenu");
  });
}

let sidebar = document.querySelector(".sidebar");
let sidebarBtn = document.querySelector(".bx-menu");
console.log(sidebarBtn);
sidebarBtn.addEventListener("click", ()=>{
  sidebar.classList.toggle("close");
});

var btn = document.getElementById('btn')

function leftClick() {
	btn.style.left = '0'
  window.location.href = '/mda_dashboard';
}

function rightClick() {
	btn.style.left = '80px'
  window.location.href = '/dia_dashboard';
}