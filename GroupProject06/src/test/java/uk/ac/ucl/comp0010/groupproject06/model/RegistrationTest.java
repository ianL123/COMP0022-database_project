package uk.ac.ucl.comp0010.groupproject06.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Test class for the Registration model.
 * Tests the creation and manipulation of registration objects that link students to modules.
 */
public class RegistrationTest {
  
  private Student student;
  private Module module;
  private Registration registration;
  
  /**
   * Sets up test data before each test.
   * Initializes a student, module, and registration object.
   */
  @BeforeEach
  void setUp() {
    student = new Student(1L, "John", "Doe", "johndoe", "john@ucl.ac.uk");
    module = new Module("COMP0010", "Software Engineering", true);
    registration = new Registration(module, student);
  }
  
  /**
   * Tests the default constructor of Registration.
   * Verifies that a new instance can be created without parameters.
   */
  @Test
  void testDefaultConstructor() {
    Registration emptyRegistration = new Registration();
    assertNotNull(emptyRegistration, "Empty registration should not be null");
  }
  
  /**
   * Tests the parameterized constructor of Registration.
   * Verifies that a new instance can be created with module and student objects.
   */
  @Test
  void testParameterizedConstructor() {
    assertNotNull(registration, "Registration should not be null");
    assertEquals(module, registration.getModule(), "Module should match");
    assertEquals(student, registration.getStudent(), "Student should match");
  }
  
  /**
   * Tests setting and getting the module of a registration.
   * Verifies that the module can be updated and retrieved correctly.
   */
  @Test
  void testSetAndGetModule() {
    Module newModule = new Module("COMP0011", "Database Systems", false);
    registration.setModule(newModule);
    assertEquals(newModule, registration.getModule(), "Module should be updated");
  }
  
  /**
   * Tests setting and getting the student of a registration.
   * Verifies that the student can be updated and retrieved correctly.
   */
  @Test
  void testSetAndGetStudent() {
    Student newStudent = new Student(2L, "Jane", "Smith", "janesmith", "jane@ucl.ac.uk");
    registration.setStudent(newStudent);
    assertEquals(newStudent, registration.getStudent(), "Student should be updated");
  }
} 