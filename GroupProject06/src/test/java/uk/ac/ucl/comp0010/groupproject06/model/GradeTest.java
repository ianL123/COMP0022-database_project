package uk.ac.ucl.comp0010.groupproject06.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Test class for the Grade model.
 * Tests the creation and manipulation of grade objects.
 */
public class GradeTest {

  private Grade grade;
  private Module module;
  private Student student;

  /**
   * Sets up test data before each test.
   * Initializes a grade, module, and student object.
   */
  @BeforeEach
  void setUp() {
    module = new Module("CS101", "Introduction to Computer Science", true);
    grade = new Grade(85, module);
    student = new Student(1L, "John", "Doe", "jdoe", "jdoe@example.com");
  }

  /**
   * Tests getting the score from a grade.
   * Verifies that the correct score is returned.
   */
  @Test
  void testGetScore() {
    assertEquals(85, grade.getScore());
  }

  /**
   * Tests getting the module from a grade.
   * Verifies that the correct module is returned.
   */
  @Test
  void testGetModule() {
    assertEquals(module, grade.getModule());
  }

  /**
   * Tests setting the score of a grade.
   * Verifies that the score is updated correctly.
   */
  @Test
  void testSetScore() {
    grade.setScore(90);
    assertEquals(90, grade.getScore());
  }

  /**
   * Tests setting the module of a grade.
   * Verifies that the module is updated correctly.
   */
  @Test
  void testSetModule() {
    Module newModule = new Module("CS102", "Data Structures", true);
    grade.setModule(newModule);
    assertEquals(newModule, grade.getModule());
  }

  /**
   * Tests the default constructor.
   * Verifies that a new grade has null values for all fields.
   */
  @Test
  void testDefaultConstructor() {
    Grade defaultGrade = new Grade();
    assertNull(defaultGrade.getScore());
    assertNull(defaultGrade.getModule());
    assertNull(defaultGrade.getStudent());
  }

  /**
   * Tests setting the student of a grade.
   * Verifies that the student is updated correctly.
   */
  @Test
  void testSetStudent() {
    grade.setStudent(student);
    assertEquals(student, grade.getStudent());
  }
  
  /**
   * Tests getting the ID of a grade.
   * Verifies that the default ID is 0.
   */
  @Test
  void testGetId() {
    assertEquals(0, grade.getId());
  }
}

