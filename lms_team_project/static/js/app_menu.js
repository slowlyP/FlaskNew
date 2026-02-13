function toggleAppMenu(){

    const menu =
        document.getElementById("appDropdown");

    if(menu.style.display === "block"){
        menu.style.display = "none";
    }else{
        menu.style.display = "block";
    }
}


/* 바깥 클릭 시 닫힘 */
window.addEventListener("click", function(e){

    const menu = document.getElementById("appDropdown");
    const icon = document.querySelector(".app-icon");

    if(!icon.contains(e.target) &&
       !menu.contains(e.target)){

        menu.style.display = "none";
    }

});
