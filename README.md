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
- Try the premium toggle and job matching modal.

All profiles, scores, and recommendations are demo data. Application, enrollment, and outreach buttons display demonstration alerts.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Default site entry point; redirects to the prototype. |
| `linkedin_skillsbridge_prototype_skill_tags.html` | Complete application markup, styling, demo data, and JavaScript. Make prototype changes here. |

## External resources

Internet access is required for Tailwind CSS (`cdn.tailwindcss.com`), Chart.js (`cdn.jsdelivr.net`), Font Awesome (`cdnjs.cloudflare.com`), and profile images (`images.unsplash.com`). If these resources are blocked, styling, charts, icons, or images may fail to load.

## Validation

There is no automated test suite or build configuration in the repository. After making changes, serve the site and check that the root page opens the prototype, charts render, career goals update, filters work, and view switching and the job modal behave correctly. Check the browser console for errors.
