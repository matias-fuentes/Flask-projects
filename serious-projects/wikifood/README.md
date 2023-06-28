[Final Project](https://cs50.harvard.edu/college/2020/fall/project/#final-project)
==================================================================================

WEBPAGE: https://cs50-wikifood.vercel.app

VIDEO PRESENTATION: https://www.youtube.com/watch?v=gO3a_suqdls

HOW I'VE MADE IT: https://www.youtube.com/watch?v=AwaIReEUcrU

## Description

Hey! Hello! And welcome to WikiFood. Where you can find all about your favourite foods, in just one place.

WikiFood it's a wiki about gastronomy. Maybe you want to know how much a dish costs? You got it. You wanna know how much time does that dish need to be prepared? You also got it. A recipe? Welp, you got it! Everything from information about any specific recipe, to even videos about how to make those recipes, you'll find it.

This page works with a free API called Spoonacular. This is where I've collected all the information about all the different foods. Without them, this could has not been possible. More information about them and its API on: https://spoonacular.com/food-api

But hey! There's much more! You can even create your account, personalize it at your own choice, see if some wine could go well with some recipe, and even more; save your favourite articles!

### So, what are you waiting for? Come to WikiFood! And be part of the kitchen.

![WikiFood preview](https://github.com/matias-fuentes/WikiFood/assets/70669575/9a41f6c0-0da6-4522-b8a9-2c303db0c1a2)

Like to see some of [last year's final projects](https://cs50.harvard.edu/college/2020/fall/#gallery-of-final-projects)?

-   [Ideas](https://cs50.harvard.edu/college/2020/fall/project/#ideas)
-   [Combining Courses](https://cs50.harvard.edu/college/2020/fall/project/#combining-courses)
-   [Specifications](https://cs50.harvard.edu/college/2020/fall/project/#specifications)
    -   [Proposal](https://cs50.harvard.edu/college/2020/fall/project/#proposal)
    -   [Status Report](https://cs50.harvard.edu/college/2020/fall/project/#status-report)
    -   [Implementation](https://cs50.harvard.edu/college/2020/fall/project/#implementation)
        -   [How to Submit](https://cs50.harvard.edu/college/2020/fall/project/#how-to-submit)
            -   [Step 1 of 2](https://cs50.harvard.edu/college/2020/fall/project/#step-1-of-2)
            -   [Step 2 of 2](https://cs50.harvard.edu/college/2020/fall/project/#step-2-of-2)

The climax of this course is its final project. The final project is your opportunity to take your newfound savvy with programming out for a spin and develop your very own piece of software. So long as your project draws upon the course's lessons, the nature of your project is entirely up to you, albeit subject to the staff's approval. You may implement your project in any language(s) as long as the staff approves. You are welcome to utilize any infrastructure, provided the staff ultimately has access to any hardware and software that your project requires. All that we ask is that you build something of interest to you, that you solve an actual problem, that you impact campus, or that you change the world. Strive to create something that outlives this course.

Inasmuch as software development is rarely a one-person effort, you are allowed an opportunity to collaborate with one or two classmates for this final project. Needless to say, it is expected that every student in any such group contribute equally to the design and implementation of that group's project. Moreover, it is expected that the scope of a two- or three-person group's project be, respectively, twice or thrice that of a typical one-person project. A one-person project, mind you, should entail more time and effort than is required by each of the course's problem sets. Although no more than three students may design and implement a given project, you are welcome to solicit advice from others, so long as you respect the course's policy on academic honesty.

Extensions on the final project are not ordinarily granted, except in cases of emergency.

## Ideas

Here are just some of the possibilities. Discuss any and all with the the staff! And if you'd like to solicit collaborators for an idea you have, do post in the course's [Q&A](https://vault.cs50.io/6027a62f-c1c6-42db-8b79-25c3e09eb10c) forum!

-   a web-based application using JavaScript, Python, and SQL
-   an iOS app using Swift
-   a game using Lua with LÖVE
-   an Android app using Java
-   a Chrome extension using JavaScript
-   a command-line program using C
-   a hardware-based application for which you program some device
-   ...

## Combining Courses

If taking some other course this semester that has a final project, you are welcome and encouraged to combine this course's project and that course's project into one, toward an end of applying lessons learned in CS50 to some other field, so long as the joint project satisfies this course's and that course's expectations. Before pursuing a joint project, though, you must disclose to both courses and receive approval from both courses.

## Specifications

Extensions on the final project are not granted, except in cases of emergency.

### Proposal

*due by Wednesday, November 18, 2020, 1:59 AM GMT-3[](https://time.cs50.io/2020-11-17T23:59:00-05:00)*

The proposal is your opportunity to receive approval and counsel from the staff before you proceed to design. If collaborating with one or two classmates, each of you should submit a proposal, even if identical.

The staff will either approve your proposal or require modifications on your part for subsequent approval. Your proposal, even if approved, is not binding; you may alter your plan at any point, provided you obtain the staff's approval for any modifications. Projects submitted without approval may not receive credit.

Here's how to complete your proposal.

Log into [CS50 IDE](https://ide.cs50.io/) and then, in a terminal window:

1.  Execute `cd` to ensure that you're in `~/` (i.e., your home directory).
2.  If you haven't already, execute `mkdir project` to make (i.e., create) a directory called `project` in your home directory.
3.  Execute `cd project` to change into (i.e., open) that directory.
4.  Execute `wget https://cdn.cs50.net/2020/fall/project/proposal.zip` to download a (compressed) ZIP file.
5.  Execute `unzip proposal.zip` to uncompress that file.
6.  Execute `rm proposal.zip` followed by `yes` or `y` to delete that ZIP file.
7.  Execute `ls`. You should see a directory called `proposal`, which was inside of that ZIP file.
8.  Execute `cd proposal` to change into that directory.
9.  Execute `ls`. You should see a file called `README.md` therein.

Edit that file in CS50 IDE, answering the questions therein. To submit your proposal, follow these instructions.

1.  Download your proposal's `README.md` file by control-clicking on the file in CS50 IDE's file browser and choosing Download.
2.  Go to CS50's [Gradescope page](https://www.gradescope.com/courses/157004).
3.  Click "Final Project: Proposal".
4.  Drag and drop your `README.md` file to the area that says "Drag & Drop".
5.  Click "Upload".

You should see a message that says "Final Project: Proposal submitted successfully!"

### Status Report

*due by Tuesday, December 1, 2020, 1:59 AM GMT-3[](https://time.cs50.io/2020-11-30T23:59:00-05:00)*

Not only is the status report intended to keep the staff apprised of your progress, it is an opportunity to keep yourself on track. If collaborating with one or two classmates, each of you should submit a status report, even if identical.

Here's how to complete your status report. Log into [CS50 IDE](https://ide.cs50.io/) and then, in a terminal window:

1.  Execute `cd` to ensure that you're in `~/` (i.e., your home directory).
2.  If you haven't already, execute `mkdir project` to make (i.e., create) a directory called `project` in your `workspace` directory.
3.  Execute `cd project` to change into (i.e., open) that directory.
4.  Execute `wget https://cdn.cs50.net/2020/fall/project/status.zip` to download a (compressed) ZIP file.
5.  Execute `unzip status.zip` to uncompress that file.
6.  Execute `rm status.zip` followed by `yes` or `y` to delete that ZIP file.
7.  Execute `ls`. You should see a directory called `status`, which was inside of that ZIP file.
8.  Execute `cd status` to change into that directory.
9.  Execute `ls`. You should see a file called `status.md` therein.

Edit that file in CS50 IDE, answering the questions therein. To submit your status report, follow these instructions.

1.  Download your status report's `status.md` file by control-clicking on the file in CS50 IDE's file browser and choosing Download.
2.  Go to CS50's [Gradescope page](https://www.gradescope.com/courses/157004).
3.  Click "Final Project: Status Report".
4.  Drag and drop your `status.md` file to the area that says "Drag & Drop".
5.  Click "Upload".

You should see a message that says "Final Project: Status Report submitted successfully!"

### Implementation

*due by Thursday, December 10, 2020, 1:59 AM GMT-3[](https://time.cs50.io/2020-12-09T23:59:00-05:00)*

Ultimately due are implementation and documentation of your final project. Your submission thereof must include all of the below.

1.  Documentation for your project in the form of a Markdown file called `README.md`. This documentation is to be a user's manual for your project. Though the structure of your documentation is entirely up to you, it should be incredibly clear to the staff how and where, if applicable, to compile, configure, and use your project. Your documentation should be at least several paragraphs in length. It should not be necessary for us to contact you with questions regarding your project after its submission. Hold our hand with this documentation; be sure to answer in your documentation any questions that you think we might have while testing your work.
2.  A "design document" for your project in the form of a Markdown file called `DESIGN.md` that discusses, technically, how you implemented your project and why you made the design decisions you did. Your design document should be at least several paragraphs in length. Whereas your documentation is meant to be a user's manual, consider your design document your opportunity to give the staff a technical tour of your project underneath its hood.
3.  Any and all files required to run your software (even if intended for some infrastructure other than CS50 IDE), including source code as well as, if applicable, configuration files, Makefiles, sample inputs, SQLite databases, and so forth. Needless to say, all source code should be thoroughly commented.
4.  A short video (that's no more than 2 minutes in length) in which you present your project to the world, as with slides, screenshots, voiceover, and/or live action. Your video should somehow include your project's title, your name and year, your dorm/house and concentration, and any other details that you'd like to convey to viewers. See [CS171's tips on how to make a "screencast"](http://www.cs171.org/2015/screencast/) though you're welcome to use an actual camera. Upload your video to YouTube as "public" or "unlisted" and include the URL of the video in your README.md file.

#### How to Submit

If you have collaborated with one or two other students, each of you should submit via this same process.

If your project requires (for execution and testing) hardware or software other than that offered by CS50 IDE, be sure that the the staff are aware of and have approved your project's needs.

##### Step 1 of 2

1.  Download a ZIP file of your final project by control-clicking on the project folder in CS50 IDE's file browser and choosing Download. (If you created your final project outside of CS50 IDE, you should still create a ZIP file of the project folder.)
2.  Go to CS50's [Gradescope page](https://www.gradescope.com/courses/157004).
3.  Click "Final Project: Implementation".
4.  Drag and drop your ZIP file to the area that says "Drag & Drop".
5.  Click "Upload".

You should see a message that says "Final Project: Implementation submitted successfully!"

##### Step 2 of 2

Submit [this form](https://forms.cs50.io/2020/fall/project/harvard).

This last form is on the longer side, so no worries if you start it before the deadline but finish a bit after.

And that's it; you've finished. This was CS50!
