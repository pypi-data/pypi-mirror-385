$(document).ready(function () {
    $("[data-level]").each(function (index) { 
        var level=$(this).attr('data-level');
        $(this).parent(".section").addClass('rst-level rst-level-'+level);
    });


    if (document.querySelector('.learnmorenote-type .course-content ')) {
        var allNodes = document.querySelectorAll('.learnmorenote-type .course-content ');
        for (var i = 0; i < allNodes.length; i++) {
            hideContent(allNodes[i])
            allNodes[i].children[0].addEventListener("click", function () {
                this.classList.toggle('expanded');
                toggleVisible(this.parentNode);
            })
        }
    }
});

function toggleVisible(learnDiv) {
    const contentParagraph = learnDiv.querySelectorAll(':scope > *:not(:first-child)');

    contentParagraph.forEach((child) => {
        child.style.display = (child.style.display === 'none' || !child.style.display) ? 'block' : 'none';
    });
}

function hideContent(learnDiv) {
    const contentParagraph = learnDiv.querySelectorAll(':scope > *:not(:first-child)');

    if (contentParagraph.length == 0) {
        var titleParaghraph = document.createElement("p");
        learnDiv.prepend(titleParaghraph);
    }

    // Toggle vidljivost za svako dete osim prvog
    contentParagraph.forEach((child) => {
        child.style.display = 'none';
    });

}