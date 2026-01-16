package uk.ac.ucl.comp0010.groupproject06.model;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import uk.ac.ucl.comp0010.groupproject06.exception.NoGradeAvailableException;
import uk.ac.ucl.comp0010.groupproject06.exception.NoRegistrationException;


/**
 * Test class for the Student model.
 * Tests the creation and manipulation of student objects, including grade and registration management.
 */
public class StudentTest {
  
  private Student student;
  private Module module;
  private Grade grade;
  private Registration registration;
  
  /**
   * Sets up test data before each test.
   * Initializes a student, module, grade, and registration objects.
   */
  @BeforeEach
  void setUp() {
    student = new Student(1L, "John", "Doe", "johndoe", "john@ucl.ac.uk");
    module = new Module("COMP0010", "Software Engineering", true);
    grade = new Grade(85, module);
    registration = new Registration(module, student);
  }
  
  /**
   * Tests the default constructor of Student.
   * Verifies that a new instance can be created without parameters.
   */
  @Test
  void testDefaultConstructor() {
    Student emptyStudent = new Student();
    assertNotNull(emptyStudent, "Empty student should not be null");
  }
  
  /**
   * Tests the parameterized constructor of Student.
   * Verifies that a new instance can be created with all required fields.
   */
  @Test
  void testParameterizedConstructor() {
    assertNotNull(student, "Student should not be null");
    assertEquals(1L, student.getId(), "ID should match");
    assertEquals("John", student.getFirstName(), "First name should match");
    assertEquals("Doe", student.getLastName(), "Last name should match");
    assertEquals("johndoe", student.getUsername(), "Username should match");
    assertEquals("john@ucl.ac.uk", student.getEmail(), "Email should match");
  }
  
  /**
   * Tests adding and retrieving grades for a student.
   * Verifies that grades can be added and retrieved correctly.
   */
  @Test
  void testAddAndGetGrades() {
    student.addGrade(grade);
    List<Grade> grades = student.getGrades();
    
    assertNotNull(grades, "Grades list should not be null");
    assertEquals(1, grades.size(), "Should have one grade");
    assertEquals(grade, grades.get(0), "Grade should match");
  }
  
  /**
   * Tests registering a module for a student.
   * Verifies that registrations can be added and retrieved correctly.
   */
  @Test
  void testRegisterModule() throws NoRegistrationException {
    student.registerModule(registration);
    List<Registration> registrations = student.getRegistrations();
    
    assertNotNull(registrations, "Registrations list should not be null");
    assertEquals(1, registrations.size(), "Should have one registration");
    assertEquals(registration, registrations.get(0), "Registration should match");
  }
  
  /**
   * Tests getting student name components.
   * Verifies that first and last names are returned correctly.
   */
  @Test
  void testGetNames() {
    assertEquals("John", student.getFirstName(), "First name should match");
    assertEquals("Doe", student.getLastName(), "Last name should match");
  }
  
  /**
   * Tests setting and getting individual fields of a student.
   * Verifies that all fields can be updated and retrieved correctly.
   */
  @Test
  void testSettersAndGetters() {
    student.setId(2L);
    student.setFirstName("Jane");
    student.setLastName("Smith");
    student.setUsername("janesmith");
    student.setEmail("jane@ucl.ac.uk");
    
    assertEquals(2L, student.getId(), "ID should be updated");
    assertEquals("Jane", student.getFirstName(), "First name should be updated");
    assertEquals("Smith", student.getLastName(), "Last name should be updated");
    assertEquals("janesmith", student.getUsername(), "Username should be updated");
    assertEquals("jane@ucl.ac.uk", student.getEmail(), "Email should be updated");
  }
  
  /**
   * Tests that the grades list is initialized.
   * Verifies that the grades list is empty but not null when a student is created.
   */
  @Test
  void testGradesInitialization() {
    List<Grade> grades = student.getGrades();
    assertNotNull(grades, "Grades list should not be null");
    assertTrue(grades.isEmpty(), "Grades list should be empty");
  }
  
  /**
   * Tests that the registrations list is initialized.
   * Verifies that the registrations list is empty but not null when a student is created.
   */
  @Test
  void testRegistrationsInitialization() {
    List<Registration> registrations = student.getRegistrations();
    assertNotNull(registrations, "Registrations list should not be null");
    assertTrue(registrations.isEmpty(), "Registrations list should be empty");
  }

  @Test
  void testGetGradeWithExistingModule() throws NoGradeAvailableException {

     NoGradeAvailableException exception = assertThrows(NoGradeAvailableException.class, 
        () -> student.getGrade(module), 
        "Expected NoGradeAvailableException to be thrown");

    assertTrue(exception.getMessage().contains("No grade available for module"),
        "Exception message should indicate no grade is available");
    assertTrue(exception.getMessage().contains(module.getCode()),
        "Exception message should include the module code");
    assertTrue(exception.getMessage().contains(String.valueOf(student.getId())),
        "Exception message should include the student ID");
  }
@Test
void testFilterWithoutMatchingModule() {
  // Arrange

  Module module1 = new Module("COMP000", "Software ineering", true);
  Module module2 = new Module("COMP001", "Software Engering", true);

  student.addGrade(grade);

  // Act & Assert
  NoGradeAvailableException exception = assertThrows(NoGradeAvailableException.class, 
      () -> student.getGrade(module2), 
      "Expected NoGradeAvailableException to be thrown");

  assertTrue(exception.getMessage().contains("No grade available for module"),
      "Exception message should indicate no grade is available");
  assertTrue(exception.getMessage().contains(module2.getCode()),
      "Exception message should include the unmatched module code");
}
@Test
void testFilterWithMatchingModule() throws NoGradeAvailableException {
  
  student.addGrade(grade);

  // Act
  Grade result = student.getGrade(module);

  // Assert
  assertNotNull(result, "Filter should find a matching grade for the module");
  assertEquals(module, result.getModule(), "The module of the grade should match the expected module");
}
} 