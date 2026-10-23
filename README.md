# LinkedIn SkillsBridge

A browser-based career growth prototype with skill gap charts, career goal selection, learning and networking recommendations, and a recruiter view.

## Run locally

From the repository directory, start a static server with Python 3:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open the server's root address, `http://127.0.0.1:8000/`, in your browser. `index.html` redirects to the prototype. Stop the server with `Ctrl+C`.

No package installation, build step, backend, database, or API keys are required. You can also open the prototype HTML file directly in a browser.

## Explore the prototype

- Select a career goal to update the skill charts and recommendations.
- Filter recommendations by skill or by Learn, Practice, and Connect categories.
- Switch between jobseeker and recruiter views.
- With Premium off, choose **Apply For Jobs Now** to browse fictional jobs for your selected role, search listings, save jobs during the session, and preview an application.
- With Premium on, choose **AUTO-MATCH** to open the SkillsBridge score-matched job modal.

All profiles, scores, recommendations, and job listings are demo data. Applications are not submitted; actions display demonstration alerts or feedback. Saved jobs last only until the page is reloaded.

The merged prototype retains the deployed 0–7 competency charts, skill pills, related-skill tags, Learn/Practice/Connect filters, and existing views. It also includes both membership-specific job flows from the CTA version. The uploaded fourth role's percentage values are normalized to the same 0–7 competency scale.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Default site entry point; redirects to the prototype. |
| `linkedin_skillsbridge_prototype_skill_tags.html` | Complete application markup, styling, demo data, and JavaScript. Make prototype changes here. |

Keep future CTA and skills changes together in this application file; the root entry point already opens the merged version.

## External resources

Internet access is required for Tailwind CSS (`cdn.tailwindcss.com`), Chart.js (`cdn.jsdelivr.net`), Font Awesome (`cdnjs.cloudflare.com`), and profile images (`images.unsplash.com`). If these resources are blocked, styling, charts, icons, or images may fail to load.

## Validation

Browser regression tests cover both membership flows, all four career goals, competency charts, related-skill tags, filters, job search/save/application preview, existing views, and mobile job browsing. They start their own local server and require access to the external resources listed above.

To install the optional test tools and run the tests:

```sh
python3 -m pip install playwright
python3 -m playwright install --with-deps chromium
python3 -m unittest discover -s tests -v
```

The tests use system Chromium when available, otherwise Playwright's installed browser. If Chromium is already installed, its download step can be omitted. Keep HTTPS certificate verification enabled; environments using an HTTPS proxy may need their trusted proxy CA registered in Chromium's certificate store.

There is no application build step. For a manual check, serve the site, try both Premium settings and all four career goals, confirm tags and filters still work, and check the browser console for errors.
