package uk.ac.ucl.comp0010.groupproject06.model;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import uk.ac.ucl.comp0010.groupproject06.exception.NoGradeAvailableException;

class ModuleTest {

  private Module module;

  @BeforeEach
  void setUp() {
    module = new Module("CS101", "Introduction to Computer Science", true);
  }

  @Test
  void testGetCode() {
    assertEquals("CS101", module.getCode());
  }

  @Test
  void testGetName() {
    assertEquals("Introduction to Computer Science", module.getName());
  }

  @Test
  void testIsMnc() {
    assertTrue(module.isMnc());
  }

  @Test
  void testSetCode() {
    module.setCode("CS102");
    assertEquals("CS102", module.getCode());
  }

  @Test
  void testSetName() {
    module.setName("Data Structures");
    assertEquals("Data Structures", module.getName());
  }

  @Test
  void testSetMnc() {
    module.setMnc(false);
    assertFalse(module.isMnc());
  }

  @Test
  void testDefaultConstructor() {
    Module defaultModule = new Module();
    assertNull(defaultModule.getCode());
    assertNull(defaultModule.getName());
    assertFalse(defaultModule.isMnc());
  }

  @Test
  void testGetId() {
    assertEquals("CS101", module.getId());
  }

  @Test
  void testComputeAverageGradeWithGrades() throws NoGradeAvailableException {
    Module module = new Module("COMP0010", "Software Engineering", true);
    Grade grade1 = new Grade(85, module);
    Grade grade2 = new Grade(75, module);
    Grade grade3 = new Grade(90, module);

    module.setGrades(List.of(grade1, grade2, grade3));
    Float average = module.computeAverageGrade();

    assertEquals(83.33, average, 0.01); // Allow small margin for floating-point errors
  }

  @Test
  void testComputeAverageGradeNoGrades() {
    Module module = new Module("COMP0010", "Software Engineering", true);

    Exception exception = assertThrows(NoGradeAvailableException.class, module::computeAverageGrade);
    assertEquals("No grades available for module: COMP0010", exception.getMessage());
  }

  @Test
  void testGetGrades(){
    Module module = new Module("COMP0010", "Software Engineering", true);
    Grade grade1 = new Grade(85, module);
    Grade grade2 = new Grade(75, module);
    Grade grade3 = new Grade(90, module);

    module.setGrades(List.of(grade1, grade2, grade3));
    List<Grade> grades = module.getGrades();

    assertEquals(3, grades.size());
    assertTrue(grades.contains(grade1));
    assertTrue(grades.contains(grade2));
    assertTrue(grades.contains(grade3));    
  }
}
