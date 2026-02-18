
function editComment(id){
    document.getElementById("content-"+id).style.display="none";
    document.getElementById("edit-form-"+id).style.display="block";
}

function cancelEdit(id){
    document.getElementById("content-"+id).style.display="block";
    document.getElementById("edit-form-"+id).style.display="none";
}

