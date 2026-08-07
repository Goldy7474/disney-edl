name: Update Disney EDL IPs

on:
  schedule:
    - cron: '0 */12 * * *' # הרצה אוטומטית פעמיים ביום
  workflow_dispatch: # מאפשר הרצה ידנית

jobs:
  update-edl:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Run ASN Resolution Script
        run: python update_ips.py

      - name: Commit and Push if Changed
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "auto: update Disney+ IP list"
          file_pattern: "disney_ips.txt"
