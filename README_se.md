# Coursework for software engineering
Student Grade Management Program by G-06 for COMP0010 Software  
Done for coursework and cooperate with two classmates.  
The PDF is the individual report.

## Test to Pass
`mvn compile test checkstyle:check spotbugs:check verify site`  

## Starting instructions
You will need two terminal instances: one each for frontend and backend.  

Instance 1 (frontend):
```
cd cw-frontend-javascript
npm ci
npm audit fix (if asked)
npm run dev
```

Instance 2 (backend):
```
cd GroupProject06
mvn spring-boot:run
```
Alternatively. `mvn spring-boot:run "-Dspring-boot.run.arguments=--app.load-sample-data=true"` (see details below)



**Frontend: Default Command**  
|Location|commands|is default?|
|-|-|-|
|cw-frontend-javascript|`npm ci` then `npm run dev`|Yes|

**Backend: Default Command**  
|Location|commands|is default?|
|-|-|-|
|GroupProject06|`mvn spring-boot:run`|Yes|

#### FINAL Branch
**Default Branch Name**  
`main` as default.

## Prefill with data
For development purposes, we have added a means to initialise the backend prefilled with a combination of Modules, Students, and Grades.
You may find this useful if you want to observe features such as average grade without having to manually add the data yourself first.
To start this you can either:
- start the backend with `mvn spring-boot:run "-Dspring-boot.run.arguments=--app.load-sample-data=true"` instead of `mvn spring-boot:run`, or
- configure `GroupProject06\src\main\resources\application.properties` so that `app.load-sample-data=true` (false by default). Then you can run it normally with `mvn spring-boot:run`

Data is generated at:
`G-06\GroupProject06\src\main\java\uk\ac\ucl\comp0010\groupproject06\config\DataLoader.java`

## About the project
This is a full stack project with the frontend and backend clearly separated.
The frontend can be found in `cw-frontend-javascript`, and backend in `GroupProject06`.
By default, we use an automatically assigned port (defaults to 5173) for the frontend and 2800 for the backend. If you want to change the backend port, configure the files below:  
`/GroupProject06/src/main/resources/application.properties`  
`/GroupProject06/cw-frontend-javascript/src/config.js`  

## We have added the following extensions beyond the basic UML implementation:
1. Various logic to ensure robustness of the program, such as:  
    - Extensive search capabilities for Modules, Student, and Grades
    - Edit and Delete Functions for Modules, Student, and Grades
    - Compute average score per Student
    - Compute average score per Module
    - Enforced link between Registration and Grades such that grades can only be added for modules that the student is registered to.
    - Specific technical requirements e.g. email must include @ symbol, ID must be a valid number, "please fill in all fields" etc. 
    - Preventing duplicates from entering the database.
2. Frontend adjustments:
    - A new statistics page for averages per student and module.
    - Present student list as “ID cards” for better design.
3. A means to populate the database with sample data upon backend initialisation.
