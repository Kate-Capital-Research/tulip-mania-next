---
html_theme.sidebar_secondary.remove: true
---

<style>
/* Make content wider for this dashboard page */
.bd-content {
    max-width: 101%;
    width: 100%;
}

/* Responsive iframe wrapper */
.risk-iframe-wrapper {
    width: 100%;
    margin: 2rem 0;
}

.risk-iframe-wrapper iframe {
    width: 100%;
    height: 80vh; /* 80% of viewport height - fully responsive */
    border: none;
}

</style>

## Performance

<div class="risk-iframe-wrapper">
  <iframe src="https://tulip.katecapllc.com/lotus/performance?embed=true" title="Lotus"></iframe>
</div>