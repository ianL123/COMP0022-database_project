package uk.ac.ucl.comp0010.groupproject06.config;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import uk.ac.ucl.comp0010.groupproject06.model.Grade;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.model.Registration;
import uk.ac.ucl.comp0010.groupproject06.model.Student;
import uk.ac.ucl.comp0010.groupproject06.repository.GradesRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.RegistrationRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.StudentRepository;

/**
 * Dataloader class to (optionally) prefill the database with sample data.
 * By setting `app.load-sample-data=true`
 * which could use the command
 * `mvn spring-boot:run "-Dspring-boot.run.arguments=--app.load-sample-data=true"`
 * Student and modules would be prefilled.
 * Registration would be randomly set and grade would be randomly generate base on it.
 */
@Component
public class DataLoader implements CommandLineRunner {

  @Value("${app.load-sample-data:false}")
  private boolean loadSampleData;

  @Autowired
  private StudentRepository studentRepository;

  @Autowired
  private ModuleRepository moduleRepository;

  @Autowired
  private GradesRepository gradesRepository;

  @Autowired
  private RegistrationRepository registrationRepository;

  private final Random random = new Random();

  @Override
  public void run(String... args) {
    if (loadSampleData) {
      loadModules();
      loadStudents();
      createRegistrationsAndGrades();
    }
  }

  private void loadModules() {
    List<Module> modules = new ArrayList<>();
    String[] moduleNames = {
      "Software Engineering", "Database Systems", "Computer Networks",
      "Operating Systems", "Artificial Intelligence", "Machine Learning",
      "Computer Graphics", "Web Development", "Mobile Computing",
      "Cybersecurity", "Cloud Computing", "Data Structures",
      "Algorithms", "Computer Architecture", "Digital Logic",
      "Programming Languages", "Software Testing", "Computer Vision",
      "Natural Language Processing", "Distributed Systems"
    };

    for (int i = 0; i < 20; i++) {
      String code = String.format("COMP%04d", i + 1);
      boolean isMnc = random.nextBoolean();
      modules.add(new Module(code, moduleNames[i], isMnc));
    }

    moduleRepository.saveAll(modules);
  }

  private void loadStudents() {
    List<Student> students = new ArrayList<>();
    String[] firstNames = {"John", "Emma", "Michael", "Sophia", "William", "Olivia", "James", "Ava",
        "Alexander", "Isabella"};

    String[] lastNames = {"Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez"};

    for (long i = 1; i <= 200; i++) {
      String firstName = firstNames[random.nextInt(firstNames.length)];
      String lastName = lastNames[random.nextInt(lastNames.length)];
      String username = firstName.toLowerCase() + lastName.toLowerCase() + i;
      String email = username + "@ucl.ac.uk";

      Student student = new Student(i, firstName, lastName, username, email);
      students.add(student);
    }

    studentRepository.saveAll(students);
  }

  private void createRegistrationsAndGrades() {
    List<Student> students = studentRepository.findAll();
    List<Module> modules = (List<Module>) moduleRepository.findAll();

    for (Student student : students) {
      // Randomly select 8 modules for each student
      List<Module> selectedModules = new ArrayList<>(modules);
      java.util.Collections.shuffle(selectedModules);
      selectedModules = selectedModules.subList(0, 8);

      for (Module module : selectedModules) {
        // Create registration
        Registration registration = new Registration(module, student);
        registrationRepository.save(registration);

        // Create grade (random score between 40 and 100)
        int score = 40 + random.nextInt(61);
        Grade grade = new Grade(score, module);
        grade.setStudent(student);
        gradesRepository.save(grade);
      }
    }
  }
}
