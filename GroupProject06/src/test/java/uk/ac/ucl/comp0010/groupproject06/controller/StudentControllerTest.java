package uk.ac.ucl.comp0010.groupproject06.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.ResponseEntity;
import uk.ac.ucl.comp0010.groupproject06.exception.NoRegistrationException;
import uk.ac.ucl.comp0010.groupproject06.model.Grade;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.model.Registration;
import uk.ac.ucl.comp0010.groupproject06.model.Student;
import uk.ac.ucl.comp0010.groupproject06.repository.GradesRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.StudentRepository;

@SpringBootTest
@AutoConfigureMockMvc
class StudentControllerTest {

  @Mock
  private StudentRepository studentRepository;

  @InjectMocks
  private StudentController studentController;

  @Mock
  private ModuleRepository moduleRepository;

  @InjectMocks
  private ModuleController moduleController;

  @Mock
  private GradesRepository gradesRepository;

  @Test
  void testGetAllStudents() {
    List<Student> students =
        Arrays.asList(new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com"),
            new Student(2L, "Jane", "Smith", "janesmith", "jane.smith@example.com"));
    when(studentRepository.findAll()).thenReturn(students);

    ResponseEntity<List<Student>> response = studentController.getAllStudents();

    assertEquals(2, response.getBody().size());
    assertEquals(200, response.getStatusCodeValue());
    verify(studentRepository, times(1)).findAll();
  }

  @Test
  void testGetStudentById_Found() {
    Student student = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    when(studentRepository.findById(1L)).thenReturn(Optional.of(student));

    ResponseEntity<Student> response = studentController.getStudentById(1L);

    assertEquals(200, response.getStatusCodeValue());
    assertEquals("John", response.getBody().getFirstName());
  }

  @Test
  void testGetStudentById_NotFound() {
    when(studentRepository.findById(1L)).thenReturn(Optional.empty());

    ResponseEntity<Student> response = studentController.getStudentById(1L);

    assertEquals(404, response.getStatusCodeValue());
  }

  @Test
  void testCreateStudent() {
    Student student = new Student(null, "John", "Doe", "johndoe", "john.doe@example.com");
    Student savedStudent = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    when(studentRepository.save(student)).thenReturn(savedStudent);

    ResponseEntity<Student> response = studentController.createStudent(student);

    assertEquals(201, response.getStatusCodeValue());
    assertNotNull(response.getBody().getId());
    verify(studentRepository, times(1)).save(student);
  }

  @Test
  void testUpdateStudent_Found() {
    Student existingStudent = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    Student updatedStudent =
        new Student(1L, "John", "Smith", "johnsmith", "john.smith@example.com");

    when(studentRepository.findById(1L)).thenReturn(Optional.of(existingStudent));
    when(studentRepository.save(any(Student.class))).thenReturn(updatedStudent);

    ResponseEntity<Student> response = studentController.updateStudent(1L, updatedStudent);

    assertEquals(200, response.getStatusCodeValue());
    assertEquals("Smith", response.getBody().getLastName());
    verify(studentRepository, times(1)).save(existingStudent);
  }

  @Test
  void testUpdateStudent_NotFound() {
    when(studentRepository.findById(1L)).thenReturn(Optional.empty());
    Student updatedStudent =
        new Student(1L, "John", "Smith", "johnsmith", "john.smith@example.com");

    ResponseEntity<Student> response = studentController.updateStudent(1L, updatedStudent);

    assertEquals(404, response.getStatusCodeValue());
  }

  @Test
  void testDeleteStudent_Found() {
    when(studentRepository.existsById(1L)).thenReturn(true);

    ResponseEntity<Void> response = studentController.deleteStudent(1L);

    assertEquals(204, response.getStatusCodeValue());
    verify(studentRepository, times(1)).deleteById(1L);
  }

  @Test
  void testDeleteStudent_NotFound() {
    when(studentRepository.existsById(1L)).thenReturn(false);

    ResponseEntity<Void> response = studentController.deleteStudent(1L);

    assertEquals(404, response.getStatusCodeValue());
  }

  @Test
  void testComputeAverage_Success() throws Exception {
    Student student = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    Module module = new Module("CS101", "Introduction to Computer Science", true);
    student.addGrade(new Grade(80, module));
    student.addGrade(new Grade(90, module));

    when(studentRepository.findById(1L)).thenReturn(Optional.of(student));

    ResponseEntity<Float> response = studentController.computeAverage(1L);

    assertEquals(200, response.getStatusCodeValue());
    assertEquals(85.0f, response.getBody());
  }

  @Test
  void testComputeAverage_NoGrades() {
    Student student = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");

    when(studentRepository.findById(1L)).thenReturn(Optional.of(student));

    ResponseEntity<Float> response = studentController.computeAverage(1L);

    assertEquals(404, response.getStatusCodeValue());
  }

  @Test
  void testGetGrades_Success() {
    Student student = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    Module module = new Module("CS101", "Introduction to Computer Science", true);
    student.addGrade(new Grade(65, module));

    when(studentRepository.findById(1L)).thenReturn(Optional.of(student));

    ResponseEntity<List<Grade>> response = studentController.getGrades(1L);

    assertEquals(200, response.getStatusCodeValue());
    assertEquals(1, response.getBody().size());
    assertEquals(65, response.getBody().get(0).getScore());
  }

  @Test
  void testGetGrades_NotFound() {
    when(studentRepository.findById(1L)).thenReturn(Optional.empty());

    ResponseEntity<List<Grade>> response = studentController.getGrades(1L);

    assertEquals(404, response.getStatusCodeValue());
  }

  @Test
  void testGetRegistrations_NotFound() {
    when(studentRepository.findById(1L)).thenReturn(Optional.empty());

    ResponseEntity<List<Registration>> response = studentController.getRegistrations(1L);

    assertEquals(404, response.getStatusCodeValue());
  }

  @Test
  void testGetGrades_NoGrades() {
    Student student = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");

    when(studentRepository.findById(1L)).thenReturn(Optional.of(student));

    ResponseEntity<List<Grade>> response = studentController.getGrades(1L);

    assertEquals(200, response.getStatusCodeValue());
    assertTrue(response.getBody().isEmpty()); // No grades should be returned
  }

  @Test
  void testDeleteStudent_AlreadyDeleted() {
    when(studentRepository.existsById(1L)).thenReturn(false);

    ResponseEntity<Void> response = studentController.deleteStudent(1L);
    assertEquals(404, response.getStatusCodeValue());
  }

  @Test
  void testComputeAverage_StudentNotFound() {
    when(studentRepository.findById(1L)).thenReturn(Optional.empty());

    ResponseEntity<Float> response = studentController.computeAverage(1L);
    assertEquals(404, response.getStatusCodeValue());
  }

  @Test
  void testGetGrades_StudentNotFound() {
    when(studentRepository.findById(1L)).thenReturn(Optional.empty());

    ResponseEntity<List<Grade>> response = studentController.getGrades(1L);
    assertEquals(404, response.getStatusCodeValue());
  }

  @Test
  void testGetRegistrations_StudentFound() {
    Student student = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    when(studentRepository.findById(1L)).thenReturn(Optional.of(student));

    ResponseEntity<List<Registration>> response = studentController.getRegistrations(1L);
    assertEquals(200, response.getStatusCodeValue());
    assertTrue(response.getBody().isEmpty()); // Assuming no registrations exist
  }

  @Test
  void testCreateStudent_EmptyFirstName() {
    Student student = new Student(null, "", "Doe", "johndoe", "john.doe@example.com"); // Invalid
                                                                                       // first name

    ResponseEntity<Student> response = studentController.createStudent(student);
    assertEquals(400, response.getStatusCodeValue()); // Bad Request
  }

  @Test
  void testCreateStudent_EmptyFirstName2() {
    Student student = new Student(1L, null, "Doe", "johndoe", "john.doe@example.com"); // Invalid
                                                                                       // first name

    ResponseEntity<Student> response = studentController.createStudent(student);
    assertEquals(400, response.getStatusCodeValue()); // Bad Request
  }

  @Test
  void testUpdateStudent_EmptyFirstName() {
    Student existingStudent = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    Student updatedStudent = new Student(1L, "", "Smith", "johnsmith", "john.smith@example.com"); // Invalid
                                                                                                  // first
                                                                                                  // name

    when(studentRepository.findById(1L)).thenReturn(Optional.of(existingStudent));

    ResponseEntity<Student> response = studentController.updateStudent(1L, updatedStudent);
    assertEquals(400, response.getStatusCodeValue()); // Bad Request
  }

  @Test
  void testUpdateStudent_EmptyFirstName2() {
    Student existingStudent = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    Student updatedStudent = new Student(1L, null, "Smith", "johnsmith", "john.smith@example.com"); // Invalid
                                                                                                    // first
                                                                                                    // name

    when(studentRepository.findById(1L)).thenReturn(Optional.of(existingStudent));

    ResponseEntity<Student> response = studentController.updateStudent(1L, updatedStudent);
    assertEquals(400, response.getStatusCodeValue()); // Bad Request
  }

  @Test
  void testCreateStudent_InvalidData() {
    Student student = new Student(null, "", "Doe", "johndoe", "john.doe@example.com"); // Invalid
                                                                                       // first name
    when(studentRepository.save(any(Student.class)))
        .thenThrow(new RuntimeException("Invalid data"));

    ResponseEntity<Student> response = studentController.createStudent(student);
    assertEquals(400, response.getStatusCodeValue());
  }

  @Test
  void testUpdateStudent_InvalidData() {
    Student existingStudent = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    Student updatedStudent = new Student(1L, "", "Smith", "johnsmith", "john.smith@example.com"); // Invalid
                                                                                                  // first
                                                                                                  // name

    when(studentRepository.findById(1L)).thenReturn(Optional.of(existingStudent));

    ResponseEntity<Student> response = studentController.updateStudent(1L, updatedStudent);
    assertEquals(400, response.getStatusCodeValue());
  }

  @Test
  void testRegisterModule_Success() throws NoRegistrationException {
    Student student = new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com");
    Module module = new Module("CS101", "Introduction to Computer Science", true);
    Registration registration = new Registration(module, student);

    when(studentRepository.findById(1L)).thenReturn(Optional.of(student));

    ResponseEntity<Void> response = studentController.registerModule(1L, registration);
    assertEquals(201, response.getStatusCodeValue()); // Created
    verify(studentRepository, times(1)).save(student); // Ensure save is called
  }

  @Test
  void testRegisterModule_StudentNotFound() {
    Module module = new Module("CS101", "Introduction to Computer Science", true);
    Registration registration =
        new Registration(module, new Student(1L, "John", "Doe", "johndoe", "john.doe@example.com"));

    when(studentRepository.findById(1L)).thenReturn(Optional.empty());

    ResponseEntity<Void> response = studentController.registerModule(1L, registration);
    assertEquals(404, response.getStatusCodeValue()); // Not Found
  }

  @Test
  void testRegisterModule_DuplicateRegistration() {
    Long studentId = 1L;
    Student student = new Student(studentId, "John", "Doe", "johndoe", "john@example.com");
    Module module = new Module("CS101", "Introduction to Computer Science", true);
    Registration registration = new Registration(module, student);

    when(studentRepository.findById(studentId)).thenReturn(Optional.of(student));

    // First registration should succeed
    studentController.registerModule(studentId, registration);
    // Second registration should result in conflict
    ResponseEntity<Void> response = studentController.registerModule(studentId, registration);

    assertEquals(409, response.getStatusCodeValue());
    }

    @Test
    public void testAddGrade() throws NoRegistrationException { 
        // Mock inputs
        Long studentId = 1L;
        String moduleCode = "CS101";
        Integer score = 85;

    Map<String, String> params = Map.of(
        "student_id", studentId.toString(),
        "module_code", moduleCode,
        "score", score.toString()
    );

        // Mock entities
        Student mockStudent = new Student(studentId, "John", "Doe", "johndoe", "john@example.com");
        Module mockModule = new Module(moduleCode, "Introduction to Computer Science", true);
        Registration mockRegistration = new Registration(mockModule, mockStudent);
        mockStudent.registerModule(mockRegistration); // Register the student for the module
        Grade mockGrade = new Grade(score, mockModule);
        mockGrade.setStudent(mockStudent);

    // Mock repository behavior
    when(studentRepository.findById(studentId)).thenReturn(Optional.of(mockStudent));
    when(moduleRepository.findByCode(moduleCode)).thenReturn(Optional.of(mockModule));
    when(gradesRepository.save(any(Grade.class))).thenReturn(mockGrade);

    // Call the controller method
    ResponseEntity<Grade> response = studentController.addGrade(params);

    // Verify the result
    assertEquals(200, response.getStatusCodeValue());
    assertEquals(mockGrade, response.getBody());

    // Verify interactions
    verify(studentRepository).findById(studentId);
    verify(moduleRepository).findByCode(moduleCode);
    verify(gradesRepository).save(any(Grade.class));
  }

  @Test
  public void testAddGrade_NotRegistered() {
    // Mock inputs
    Long studentId = 1L;
    String moduleCode = "CS101";
    Integer score = 85;

    Map<String, String> params = Map.of(
        "student_id", studentId.toString(),
        "module_code", moduleCode,
        "score", score.toString()
    );

    // Mock entities
    Student mockStudent = new Student(studentId, "John", "Doe", "johndoe", "john@example.com");
    Module mockModule = new Module(moduleCode, "Introduction to Computer Science", true);
    // Note: Not adding registration to test forbidden case

    // Mock repository behavior
    when(studentRepository.findById(studentId)).thenReturn(Optional.of(mockStudent));
    when(moduleRepository.findByCode(moduleCode)).thenReturn(Optional.of(mockModule));

    // Call the controller method
    ResponseEntity<Grade> response = studentController.addGrade(params);

    // Verify the result
    assertEquals(403, response.getStatusCodeValue()); // Should be forbidden
  }

  @Test
  public void testAddGrade_StudentNotFound() {
    // Mock inputs
    Long studentId = 1L;
    String moduleCode = "CS101";
    Integer score = 85;

    Map<String, String> params = Map.of("student_id", studentId.toString(), "module_code",
        moduleCode, "score", score.toString());

    // Mock repository behavior
    when(studentRepository.findById(studentId)).thenReturn(Optional.empty());

    // Call the controller method
    ResponseEntity<Grade> response = studentController.addGrade(params);

    // Verify the result
    assertEquals(404, response.getStatusCodeValue());
    }

  @Test
  public void testAddGrade_ModuleNotFound() {
    // Mock inputs
    Long studentId = 1L;
    String moduleCode = "CS101";
    Integer score = 85;

    Map<String, String> params = Map.of("student_id", studentId.toString(), "module_code",
        moduleCode, "score", score.toString());

    // Mock entities
    Student mockStudent = new Student(studentId, "John", "Doe", "johndoe", "john@example.com");

    // Mock repository behavior
    when(studentRepository.findById(studentId)).thenReturn(Optional.of(mockStudent));
    when(moduleRepository.findByCode(moduleCode)).thenReturn(Optional.empty());

    // Call the controller method
    ResponseEntity<Grade> response = studentController.addGrade(params);

    // Verify the result
    assertEquals(404, response.getStatusCodeValue());
    }

  @Test
  public void testAddGrade_InvalidParameters() {
    // Invalid inputs
    Map<String, String> params =
        Map.of("student_id", "invalid_id", "module_code", "CS101", "score", "85");

    // Call the controller method
    ResponseEntity<Grade> response = studentController.addGrade(params);

    // Verify the result
    assertEquals(400, response.getStatusCodeValue());
    }

    @Test
    public void testAddGrade_InvalidScore() {
        // Invalid inputs
        Long studentId = 1L;
        String moduleCode = "CS101";

        Map<String, String> params = Map.of(
                "student_id", studentId.toString(),
                "module_code", moduleCode,
                "score", "-5" // Invalid score
        );

        // Call the controller method
        ResponseEntity<Grade> response = studentController.addGrade(params);

        // Verify the result
        assertEquals(404, response.getStatusCodeValue());
    }

    @Test
    public void testAddGrade_AlreadyExists() throws NoRegistrationException {
        // Mock inputs
        Long studentId = 1L;
        String moduleCode = "CS101";
        Integer score = 85;

        Map<String, String> params = Map.of(
                "student_id", studentId.toString(),
                "module_code", moduleCode,
                "score", score.toString()
        );

        // Mock entities
        Student mockStudent = new Student(studentId, "John", "Doe", "johndoe", "john@example.com");
        Module mockModule = new Module(moduleCode, "Introduction to Computer Science", true);
        Registration mockRegistration = new Registration(mockModule, mockStudent);
        mockStudent.registerModule(mockRegistration); // Register the student for the module
        Grade existingGrade = new Grade(score, mockModule);
        existingGrade.setStudent(mockStudent);
        mockStudent.addGrade(existingGrade); // Add existing grade

        // Mock repository behavior
        when(studentRepository.findById(studentId)).thenReturn(Optional.of(mockStudent));
        when(moduleRepository.findByCode(moduleCode)).thenReturn(Optional.of(mockModule));

        // Call the controller method
        ResponseEntity<Grade> response = studentController.addGrade(params);

        // Verify the result
        assertEquals(409, response.getStatusCodeValue());
    }


}
