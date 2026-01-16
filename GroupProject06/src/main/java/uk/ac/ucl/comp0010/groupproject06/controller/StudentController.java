package uk.ac.ucl.comp0010.groupproject06.controller;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import uk.ac.ucl.comp0010.groupproject06.exception.NoGradeAvailableException;
import uk.ac.ucl.comp0010.groupproject06.exception.NoRegistrationException;
import uk.ac.ucl.comp0010.groupproject06.model.Grade;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.model.Registration;
import uk.ac.ucl.comp0010.groupproject06.model.Student;
import uk.ac.ucl.comp0010.groupproject06.repository.GradesRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.StudentRepository;

/**
 * Controller for handling student requests.
 * Grade CRUD is also send to this controller.
 */
@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/students")
public class StudentController {

  @Autowired
  private StudentRepository studentRepository;

  @Autowired
  private GradesRepository gradesRepository;

  @Autowired
  private ModuleRepository moduleRepository;

  /**
   * Gets all students.
   *
   * @return a list of all students
   */
  @GetMapping
  public ResponseEntity<List<Student>> getAllStudents() {
    List<Student> students = studentRepository.findAll();
    return ResponseEntity.ok(students);
  }

  /**
   * Gets a student by their ID.
   *
   * @param id the ID of the student
   * @return the student if found, otherwise a 404 response
   */
  @GetMapping("/{id}")
  public ResponseEntity<Student> getStudentById(@PathVariable Long id) {
    Optional<Student> student = studentRepository.findById(id);
    return student.map(ResponseEntity::ok)
        .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).build());
  }

  /**
   * Creates a student.
   *
   * @param student the student to create
   * @return the created student
   */
  @PostMapping
  public ResponseEntity<Student> createStudent(@RequestBody Student student) {
    if (student.getFirstName() == null || student.getFirstName().isEmpty()) {
      return ResponseEntity.badRequest().body(null); // Return 400 for invalid data
    }

    Student savedStudent = studentRepository.save(student);
    return new ResponseEntity<>(savedStudent, HttpStatus.CREATED);
  }

  /**
   * Updates a student.
   *
   * @param id the ID of the student
   * @param updatedStudent the updated student
   * @return the updated student if found, otherwise a 400 response
   */
  @PutMapping("/{id}")
  public ResponseEntity<Student> updateStudent(
      @PathVariable Long id, @RequestBody Student updatedStudent
  ) {
    if (updatedStudent.getFirstName() == null || updatedStudent.getFirstName().isEmpty()) {
      return ResponseEntity.badRequest().build(); // Return 400 for invalid data
    }

    return studentRepository.findById(id)
      .map(existingStudent -> {
        existingStudent.setFirstName(updatedStudent.getFirstName());
        existingStudent.setLastName(updatedStudent.getLastName());
        existingStudent.setUsername(updatedStudent.getUsername());
        existingStudent.setEmail(updatedStudent.getEmail());
        Student savedStudent = studentRepository.save(existingStudent);
        return ResponseEntity.ok(savedStudent);
      })
      .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).build());
  }

  /**
   * Deletes a student.
   *
   * @param id the ID of the student
   * @return a 204 response if the student was deleted, otherwise a 404 response
   */
  @DeleteMapping("/{id}")
  public ResponseEntity<Void> deleteStudent(@PathVariable Long id) {
    if (studentRepository.existsById(id)) {
      studentRepository.deleteById(id);
      return ResponseEntity.noContent().build();
    } else {
      return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
    }
  }

  /**
   * Computes the average grade of a student.
   *
   * @param id the ID of the student
   * @return the average grade if found, otherwise a 404 response
   */
  @GetMapping("/{id}/average")
  public ResponseEntity<Float> computeAverage(@PathVariable Long id) {
    Optional<Student> student = studentRepository.findById(id);
    if (student.isPresent()) {
      try {
        Float average = student.get().computeAverage();
        return ResponseEntity.ok(average);
      } catch (NoGradeAvailableException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(null);
      }
    }
    return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
  }

  /**
   * Adds a grade to a student based on the provided parameters.
   * This would add a grade data.
   *
   * @param params a map containing the grade parameters: "student_id", "module_code", and "score"
   * @return the added grade if successful (HTTP 200), a 404 response if the student or module
   *         is not found, or a 400 response if the request parameters are invalid
   */
  @PostMapping("/{id}/grades")
  public ResponseEntity<Grade> addGrade(@RequestBody Map<String, String> params) {
    Long studentId;
    String moduleCode;
    Integer score;

    try {
      studentId = Long.valueOf(params.get("student_id"));
      moduleCode = params.get("module_code");
      score = Integer.valueOf(params.get("score"));
    } catch (NumberFormatException e) {
      return ResponseEntity.badRequest().body(null);
    }

    // Find the student by using student_id
    Student student = studentRepository.findById(studentId).orElse(null);
    if (student == null) {
      return ResponseEntity.notFound().build();
    }

    // Find the module by using module_code
    Module module = moduleRepository.findByCode(moduleCode).orElse(null);
    if (module == null) {
      return ResponseEntity.notFound().build();
    }

    // Check if student is registered for the module
    boolean isRegistered = student.getRegistrations().stream()
        .anyMatch(reg -> reg.getModule().getCode().equals(moduleCode));

    if (!isRegistered) {
      return ResponseEntity.status(HttpStatus.FORBIDDEN)
          .body(null);
    }

    // Check if a grade for this student and module already exists
    Optional<Grade> existingGrade = student.getGrades().stream()
        .filter(g -> g.getModule().equals(module))
        .findFirst();

    if (existingGrade.isPresent()) {
      // Grade already exists for this student and module
      return ResponseEntity.status(HttpStatus.CONFLICT)
            .body(null);
    }

    // Create a Grade object and set all values
    Grade grade = new Grade(score, module);
    grade.setStudent(student);

    // Save the Grade object
    Grade savedGrade = gradesRepository.save(grade);

    // Return the saved Grade object
    return ResponseEntity.ok(savedGrade);
  }

  /**
   * Registers a student to a module.
   * Actully not used but leave it here incase somehow needed.
   *
   * @param id the ID of the student
   * @param registration the registration to add
   * @return a 201 response if the registration was added, otherwise a 404 response
   */
  @PostMapping("/{id}/registrations")
  public ResponseEntity<Void> registerModule(
      @PathVariable Long id, @RequestBody Registration registration
  ) {
    Optional<Student> student = studentRepository.findById(id);
    if (student.isPresent()) {
      try {
        student.get().registerModule(registration);
        studentRepository.save(student.get());
        return ResponseEntity.status(HttpStatus.CREATED).build();
      } catch (NoRegistrationException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT).build();
      }
    }
    return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
  }

  /**
   * Gets all grades of a student.
   * the recursive structure is grades contain in a list of grade.
   * And this is a container in the student.
   *
   * @param id the ID of the student
   * @return a list of all grades if found, otherwise a 404 response
   */
  @GetMapping("/{id}/grades")
  public ResponseEntity<List<Grade>> getGrades(@PathVariable Long id) {
    Optional<Student> student = studentRepository.findById(id);
    return student.map(value -> ResponseEntity.ok(value.getGrades()))
        .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).build());
  }

  /**
   * Gets all registrations of a student.
   *
   * @param id the ID of the student
   * @return a list of all registrations if found, otherwise a 404 response
   */
  @GetMapping("/{id}/registrations")
  public ResponseEntity<List<Registration>> getRegistrations(@PathVariable Long id) {
    Optional<Student> student = studentRepository.findById(id);
    return student.map(value -> ResponseEntity.ok(value.getRegistrations()))
        .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).build());
  }
}
