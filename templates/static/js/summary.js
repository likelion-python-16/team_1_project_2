document.addEventListener("DOMContentLoaded", function () {
    const saveBtn = document.getElementById("saveBtn");
    const listBtn = document.getElementById("listBtn");

    saveBtn.addEventListener("click", function () {
        alert("저장하기 기능은 API와 연결 필요");
    });

    listBtn.addEventListener("click", function () {
        window.location.href = "/list/";
    });
});
