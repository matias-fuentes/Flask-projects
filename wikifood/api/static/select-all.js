const selectAll = document.getElementById('select-all');
const deleteBtn = document.querySelector('.saved-articles__deleteBtn');
const checkboxes = Array.from(document.querySelectorAll('.saved-articles__checkbox'));
const trs = Array.from(document.querySelectorAll('tr'));

const deleteBtnClassName = 'saved-articles__deleteBtn saved-articles__deleteBtn--selected';

selectAll.addEventListener('click', () => {
    if (selectAll.checked === true) {
        if (deleteBtn.className !== deleteBtnClassName) {
            deleteBtn.classList.add('saved-articles__deleteBtn--selected');
        }

        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });

        trs.forEach(tr => {
            if (tr.className !== 'selected') {
                tr.classList.add("selected");
            }
        })
    } else {
        if (deleteBtn.className === deleteBtnClassName) {
            deleteBtn.classList.remove('saved-articles__deleteBtn--selected');
        }

        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        trs.forEach(tr => {
            if (tr.className === 'selected') {
                tr.classList.remove("selected");
            }
        })
    }
});

checkboxes.forEach((checkbox, index) => {
    checkbox.addEventListener('click', () => {
        const headerTableRow = trs[0];
        const currentTableRow = trs[index + 1];
        const isSomeCheckboxSelected = getIsSomeCheckboxSelected();
        const isSomeCheckboxNOTSelected = getIsSomeCheckboxNOTSelected();
        if (checkbox.checked === true) {
            if (currentTableRow.className !== 'selected') {
                currentTableRow.classList.add('selected');
            }
            
            if (isSomeCheckboxSelected && deleteBtn.className !== deleteBtnClassName) {
                deleteBtn.classList.add('saved-articles__deleteBtn--selected');
            }

            if (!isSomeCheckboxNOTSelected) {
                selectAll.checked = true;
                if (headerTableRow.className !== 'selected') {
                    headerTableRow.classList.add('selected');
                }
            }
        } else {
            if (currentTableRow.className === 'selected') {
                currentTableRow.classList.remove('selected');
            }
            
            if (!isSomeCheckboxSelected) {
                selectAll.checked = false;
                if (headerTableRow.className === 'selected') {
                    headerTableRow.classList.remove('selected');
                }

                if (deleteBtn.className === deleteBtnClassName) {
                    deleteBtn.classList.remove('saved-articles__deleteBtn--selected');
                }
            }

            if (isSomeCheckboxNOTSelected) {
                selectAll.checked = false;
                if (headerTableRow.className === 'selected') {
                    headerTableRow.classList.remove('selected');
                }
            }

            if (currentTableRow.className === 'selected') {
                currentTableRow.classList.remove("selected");
            }
        }
    });
});

const getIsSomeCheckboxSelected = () => {
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked === true) {
            return true;
        }
    }
    return false;
}

const getIsSomeCheckboxNOTSelected = () => {
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked === false) {
            return true;
        }
    }
    return false;
}
