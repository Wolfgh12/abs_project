/**
 * ABS Site Loader & Cookie Management
 * Forces a 3-second display on EVERY page load.
 * Cookie duration: 15 Days.
 */
document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('site-loader');
    const progressBar = document.getElementById('loader-progress');
    const body = document.body;

    // 1. Start progress bar animation and lock scroll
    body.classList.add('loading-active');
    if (progressBar) {
        progressBar.style.width = '100%';
    }

    // 2. Force the loader to stay for exactly 3 seconds every time
    setTimeout(() => {
        if (loader) {
            loader.style.opacity = '0';
            
            // Wait for the CSS transition (700ms) to finish before removing
            setTimeout(() => {
                loader.style.display = 'none';
                body.classList.remove('loading-active');
                
                // 3. Trigger Cookie Banner logic only after loader is gone
                showCookieBanner();
            }, 700);
        }
    }, 3000); 

    // --- COOKIE BANNER LOGIC ---
    function showCookieBanner() {
        const banner = document.getElementById('cookie-banner');
        const acceptBtn = document.getElementById('accept-cookies');
        const closeBtn = document.getElementById('close-cookie-banner');

        // Check if user has already accepted cookies
        const cookiesAccepted = document.cookie.includes('cookies_accepted=true');

        if (banner && !cookiesAccepted) {
            banner.classList.remove('hidden');
            setTimeout(() => {
                banner.classList.add('show');
            }, 100);
        }

        if (acceptBtn) {
            acceptBtn.addEventListener('click', () => {
                // SET TO 15 DAYS
                const d = new Date();
                const expirationDays = 15; 
                d.setTime(d.getTime() + (expirationDays * 24 * 60 * 60 * 1000));
                
                document.cookie = "cookies_accepted=true; expires=" + d.toUTCString() + "; path=/; SameSite=Lax";
                hideBanner(banner);
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                hideBanner(banner);
            });
        }
    }

    function hideBanner(banner) {
        banner.classList.remove('show');
        setTimeout(() => {
            banner.classList.add('hidden');
        }, 800);
    }
});