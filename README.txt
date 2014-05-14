Scholaris
 
Scholaris displays the last, current and next event of an Google Calendar. Its aim is to display the most important information at one glance and is not meant to replace a real time management application.
 
Possible use case is the normal everyday life of a student or teacher, but it could also be used as an information display in the entrance area of a school or a university.

At the first start of the application it ask for permisson to access a Google calendar in the default browser. It is recommended to use an extra calendar for the events to be displayed by Scholaris. If there is more than one calendar, the right one is chosen by the hotwords listed below.

Hotwords: "college", "university", "school", "schule", "studium", "école", "ecole", "collège", "étude", "etude"

Attention: The events of the current day and the OAuth2.0 authentification data are stored in plain text.



Build requirements: - python2.7, kivy (googleapiclient, httplib2, oauth2client and uritemplate are included)
                    - an API Client ID and secret to access Google Calendar (-> data/calendar_backend.py)
                    - for python-for-android a distribution with openssl

The repository contains a precompiled APK file with a valide API client ID and secret.
