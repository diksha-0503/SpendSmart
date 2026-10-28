// Small browser-side helpers for SpendSmart.

document.addEventListener("DOMContentLoaded", function () {
    // Ask for confirmation before deleting a transaction.
    const deleteForms = document.querySelectorAll(".delete-form");

    deleteForms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const shouldDelete = confirm("Are you sure you want to delete this transaction?");
            if (!shouldDelete) {
                event.preventDefault();
            }
        });
    });
});
