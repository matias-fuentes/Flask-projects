const selectAll = document.querySelector('.th-checkbox');
const checkboxes = Array.from(document.querySelectorAll('.td-checkbox'));
const articleImages = Array.from(document.querySelectorAll('.article-img'));
const trs = Array.from(document.querySelectorAll('tr'));
trs.splice(0, 1);

let i;
if (articleImages[0] === null) {
    i = 0;
} else {
    i = 1;
}
for (i; i < articleImages.length; i++) {
    articleImages.splice(i, 1);
}

selectAll.addEventListener('click', function() {
    if (selectAll.checked) {
        $('.delete-icon').css('opacity', '1');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
    } else {
        $('.delete-icon').css('opacity', '0.6');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    }

    trs.forEach(tr => {
        if (selectAll.checked) {
            if (!tr.classList.contains("selected")) {
                tr.classList.toggle("selected");
            }
        } else {
            if (tr.classList.contains("selected")) {
                tr.classList.toggle("selected");
            }
        }
    });
});

articleImages.forEach((image, index) => {
    image.addEventListener('click', function() {
        trs[index].classList.toggle("selected");
        let j = 0;
        for (let i = 0; i < articleImages.length; i++) {
            if (trs[i].classList.contains("selected")) {
                j++;
            }
        }
        if (j === articleImages.length) {
            selectAll.checked = true;
        } else {
            selectAll.checked = false;
        }
    });
});

trs.forEach(tr => {
    tr.addEventListener('click', function() {
        for (let i = 0; i < trs.length; i++) {
            if (trs[i].classList.contains("selected")) {
                $('.delete-icon').css('opacity', '1');
                break;
            } else {
                $('.delete-icon').css('opacity', '0.6');
            }
        }
    });
})

checkboxes.forEach((checkbox, index) => {
    checkbox.addEventListener('click', function() {
        trs[index].classList.toggle("selected");

        let j = 0;
        for (let i = 0; i < checkboxes.length; i++) {
            if (trs[i].classList.contains("selected")) {
                j++;
            }
        }
        if (j === articleImages.length) {
            selectAll.checked = true;
        } else {
            selectAll.checked = false;
        }
    });
});