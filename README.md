# Feeds

#### Video Demo: [Feeds](https://youtu.be/xiFHxJbdzx4)

## Problem to Solve

Given the Information Age of 2024, we are being overwhelmed by vast amounts of web content; however, our capacity to process this information is limited. `feeds` addresses this problem by offering a simplified RSS feed reader that allows users to subscribe to multiple web feeds, aggregate content, and view it in an organized format. By automatically updating `feeds`, this application enables users to manage their web content efficiently.

While RSS feed readers are not new technology, `feeds` combines the functionality of profile creation, public/private feeds, and interactive exploration, offering users a more personalized and social experience. The `feeds` application leverages core web technologies:
* Python (Django): For handling back-end logic, user authentication, and data management.
* JavaScript: For front-end interactivity and dynamic behavior.
* Bootstrap: For responsive design and styling of the user interface.
* Python Feedparser, Schedule, and Threading Libraries: To automate the retrieval of RSS feed data and update it on a regular schedule.

## Background

The project builds on concepts from [CS50’s Web Programming with Python and JavaScript](https://cs50.harvard.edu/web/2020/) using the Django framework for the back-end and JavaScript for interactive components on the front-end, leveraging several modern web technologies to provide a smooth and responsive user experience. The stack includes:

#### Python & Django (Back-End Framework):
* Django is a high-level Python web framework that promotes rapid development and clean, pragmatic design. The Django Model-View-  Template (MVT) architecture is used to handle data storage, business logic, and user interface rendering:
    * Models: Define the data structure (e.g., User, Profile, Feed, Item). These models map directly to the database tables, managing user profiles, subscriptions, and feed items.
    * Views: Handle requests and responses. Views like index_view, profile_view, and feed_view dynamically render pages based on user  input and data from the models.
    * Templates: Use Django’s templating language to dynamically generate HTML content, ensuring that each user gets a personalized view of their feeds and profiles.
* Django's built-in authentication system (using AbstractUser) handles user registration, login, logout, and password hashing, ensuring security for user data.

#### JavaScript (Frant-End Interactivity):
* JavaScript is used to make the application interactive and responsive. It powers dynamic elements like Bootstrap modals for creating and editing profiles and feeds, improving the user experience without requiring full-page reloads.
    * JavaScript is essential for handling event-driven actions, such as user form submissions (via fetch API) and updating the UI based on server responses.
    * Single-Page Application (SPA) elements are implemented on the index page for smooth, uninterrupted navigation between feeds and items, making the user experience more fluid.
 
#### Bootstrap (Responsive User Interface):
* Bootstrap, a popular front-end framework, is used to style the application and ensure it is responsive across different devices. It provides a clean and modern design for:
    * Navigation: A responsive navbar is used for quick navigation between feeds, profiles, and account management.
    * Modals: Bootstrap modals allow users to dynamically interact with the application, such as creating and editing feeds or profiles.
    * Layout: Bootstrap grid and layout components help ensure the app is visually appealing and easy to navigate on both desktop and mobile devices.

#### RSS Feed Parsing with feedparser
* The Python feedparser library is used to retrieve and parse RSS feeds. Feedparser can handle a variety of RSS and Atom feed formats, making it easy to extract relevant information like titles, descriptions, links, and publication dates from external websites.
* Once parsed, the feed data is stored in the database as Item instances, associated with a user’s subscribed feed.

#### Task Scheduling with schedule and threading
* Python’s schedule library is used to automate the process of fetching and updating RSS feeds. The app is set up to update all user feeds daily at 7:30 AM, ensuring the content stays up-to-date without requiring manual refreshes.
* Threading is employed to run the scheduled tasks in the background, preventing the scheduled jobs from blocking the main application flow. This allows the application to continue serving users while feeds are being updated.

#### Database (SQLite / PostgreSQL)
* The application uses Django’s default SQLite database during development, but it can be easily configured to use PostgreSQL or other database systems in production environments.
* The database stores user profiles, subscribed feeds, and the items associated with each feed, with Django ORM (Object-Relational Mapping) facilitating seamless database interactions.

## Understanding

`feeds` is a web application that syndicates and aggregates RSS feed content. Below is an overview of the app’s architecture and functionality:

* Back-End (Python & Django):
    * Core models include User, Profile, Feed, and Item. Users can create profiles and subscribe to RSS feeds, which are parsed and stored as Item instances.
    * Util.py manages feed retrieval using feedparser, while the schedule and threading libraries ensure feeds are updated daily at 7:30 AM.
* Front-End (JavaScript & Bootstrap):
    * JavaScript handles dynamic content, such as creating and editing profiles and feeds through Bootstrap modals.
    * A single-page application structure is used to enhance interactivity without page reloads.
* Feed Management:
    * Users can create, edit, delete, and toggle the visibility of their feeds. The app also features a random feed exploration function where users can discover public feeds.
* Profile Management:
    * Profiles can be public or private, and users can customize their profile description and subscribed feeds.

#### How These Technologies Work Together
* User Interaction:
    * Users interact with the front-end, which is powered by JavaScript and styled with Bootstrap. Actions like creating or editing profiles and feeds are handled by JavaScript modals and sent to the back-end via AJAX requests.
* Back-End Logic:
    * Django processes the user requests. For example, when a new feed is added, Django validates the feed URL, stores the data in the database, and invokes feedparser to fetch items from the feed.
* Feed Parsing and Scheduling:
    * After a user subscribes to a feed, the back-end uses the feedparser library to extract content from the RSS URL. Then, the schedule and threading libraries ensure that feeds are updated at 7:30 AM daily without user intervention.
* Content Rendering:
    * The content (e.g., user profiles, feeds, and items) is dynamically rendered using Django templates, providing users with an up-to-date view of their feeds. Public and private feeds are managed through Django views, ensuring that only authorized users can view private feeds.

This tech stack allows `feeds` to offer a responsive, secure, and scalable platform for users to manage their RSS subscriptions and interact with content in real time.

## Specification

TODO
