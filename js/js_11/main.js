const mainT11 = () => {
	//-- Reveal animation
	const ratio = 0.01;
	const options = {
		root: null,
		rootMargin: '0px',
		threshold: ratio,
	};

	if (true) {
		const handleIntersect = function (entries, observer) {
			entries.forEach(function (entry) {
				if (entry.intersectionRatio > ratio) {
					entry.target.classList.remove('reveal');
					entry.target.classList.remove('reveal-opening-hours');
					observer.unobserve(entry.target);
				}
			});
		};

		document.documentElement.classList.add('reveal-loaded');
		const observer = new IntersectionObserver(handleIntersect, options);

		setTimeout(function () {
			d.qAll('.reveal').forEach(function (r) {
				observer.observe(r);
			});
		}, 500);
	}
};

document.onload = mainT11();
