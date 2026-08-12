# Project Rules

- After every successful git synchronization (sync), always execute the following command to trigger the GitHub Actions workflow for updating the dashboard in portfolio mode:
  `gh workflow run update_dashboard.yml -f update_mode=portfolio`
