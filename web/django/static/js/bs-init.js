
if (window.innerWidth < 768) {
	[].slice.call(document.querySelectorAll('[data-bss-disabled-mobile]')).forEach(function (elem) {
		elem.classList.remove('animated');
		elem.removeAttribute('data-bss-hover-animate');
		elem.removeAttribute('data-aos');
		elem.removeAttribute('data-bss-parallax-bg');
		elem.removeAttribute('data-bss-scroll-zoom');
	});
}

document.addEventListener('DOMContentLoaded', function() {
	const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
	const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl,  {trigger: 'hover'}));
	var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
	var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
		return new bootstrap.Popover(popoverTriggerEl);
	});

	var toastTriggers = document.querySelectorAll('[data-bs-toggle="toast"]');
        for (let toastTrigger of toastTriggers) {
            toastTrigger.addEventListener('click', function () {
                var toastSelector = toastTrigger.getAttribute('data-bs-target');
                if (!toastSelector) return;
                try {
                    var toastEl = document.querySelector(toastSelector);
                    if (!toastEl) return;
                    var toast = new bootstrap.Toast(toastEl);
                    toast.show();
                }
                catch(e) {
                    console.error(e);
                }
            });
        }
}, false);