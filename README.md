""# Tag Analytics

Tag Analytics is a powerful add-on designed to enhance your Anki workflow by providing in-depth analysis of your tag usage and card distribution. This tool helps you identify study patterns, optimize tag organization, and streamline your review process.

Features

Detailed Tag Analysis:

Displays frequency and distribution of tags across your Anki collection.

Identifies underutilized tags and potential areas for optimization.

Review Insights:

Provides insight into the number of cards reviewed for each tag.

Highlights tags with the highest and lowest review counts.

Customizable Settings:

Adjustable analysis intervals for real-time monitoring.

Select between various styles of data presentation.

Debug Logging:

Optional logging to assist in troubleshooting and optimizing performance.

Installation

Download the Add-on:

Clone this repository or download the ZIP file from GitHub.

Ensure you have the tag_analytics folder containing __init__.py.

Install in Anki:

Locate your Anki add-ons directory:

macOS: ~/Library/Application Support/Anki2/addons21/

Windows: C:\Users\<YourUser>\AppData\Roaming\Anki2\addons21\

Linux: ~/.local/share/Anki2/addons21/

Copy the tag_analytics folder to the add-ons directory.

If updating, replace the existing tag_analytics folder.

Restart Anki:

Close and reopen Anki to load the add-on.

Verify Installation:

Go to Tools → Tag Analytics Settings in Anki. If the settings dialog opens, the add-on is installed correctly.

Usage

Configure Settings:

Open Tools → Tag Analytics Settings in Anki.

Adjust the following options:

Interval: Frequency of tag analysis updates (e.g., every 10 cards).

Style: Choose between different styles of presentation (inverted, standard).

Debug Logs: Enable to troubleshoot issues (logs appear in Anki’s console).

Click "Save" to apply changes.

View Analytics:

During reviews, Tag Analytics will display real-time insights on tag usage.

Monitor which tags are underutilized or disproportionately large.

Adjust your study habits accordingly to optimize retention.

Example Configuration

Interval: 10

Style: Inverted

Target Level: Card

Debug Logs: Enabled

With this setup, tag analytics will update every 10 cards, presenting insights with an inverted color scheme.

Troubleshooting

Data Not Displaying:

Ensure the interval is set appropriately (e.g., not too high).

Check for conflicts with other add-ons. Temporarily disable them to test.

Enable debug logs in settings and review the console for errors.

Settings Dialog Errors:

Verify the tag_analytics folder contains only __init__.py from the latest version.

Restart Anki after updating the add-on.

Support the Developer

If you find this add-on helpful, consider supporting the developer via Ko-fi:

[![Support on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/mbrockman1)

Contributing

Contributions are welcome! To contribute:

Fork this repository.

Create a feature branch (git checkout -b feature/YourFeature).

Commit your changes (git commit -m "Add YourFeature").

Push to the branch (git push origin feature/YourFeature).

Open a pull request.

Please include tests and update this README if necessary.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments

Built for Anki 25.02.4 (Python 3.9.18, Qt 6.6.2, PyQt 6.6.1).

Inspired by the need for organized and efficient tag management in Anki.
""

