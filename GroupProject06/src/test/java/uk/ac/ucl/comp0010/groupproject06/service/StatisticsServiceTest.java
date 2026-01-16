package uk.ac.ucl.comp0010.groupproject06.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.when;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import uk.ac.ucl.comp0010.groupproject06.model.Grade;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.model.Student;
import uk.ac.ucl.comp0010.groupproject06.repository.StudentRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;

/**
 * Test class for the StatisticsService.
 * Tests the calculation and retrieval of student grade statistics.
 */
@ExtendWith(MockitoExtension.class)
public class StatisticsServiceTest {
  
  @Mock
  private StudentRepository studentRepository;
  
  @Mock
  private ModuleRepository moduleRepository;
  
  @InjectMocks
  private StatisticsService statisticsService;
  
  private Student student1;
  private Student student2;
  private Module module1;
  private Module module2;
  
  /**
   * Sets up test data before each test.
   * Initializes students and modules for testing grade calculations.
   */
  @BeforeEach
  void setUp() {
    // Create test data
    student1 = new Student(1L, "John", "Doe", "johndoe", "john@ucl.ac.uk");
    student2 = new Student(2L, "Jane", "Smith", "janesmith", "jane@ucl.ac.uk");
    module1 = new Module("COMP0010", "Software Engineering", true);
    module2 = new Module("COMP0011", "Database Systems", true);
  }
  
  /**
   * Tests calculating average grades for a single student with multiple grades.
   * Verifies that the average is calculated correctly.
   */
  @Test
  void testGetAverageGradePerStudent() {
    // Add grades to student1
    Grade grade1 = new Grade(80, module1);
    Grade grade2 = new Grade(90, module1);
    grade1.setStudent(student1);
    grade2.setStudent(student1);
    student1.addGrade(grade1);
    student1.addGrade(grade2);
    
    // Mock repository response
    when(studentRepository.findAll()).thenReturn(Arrays.asList(student1));
    
    // Test the service
    Map<String, Double> result = statisticsService.getAverageGradePerStudent();
    
    assertNotNull(result, "Result should not be null");
    assertEquals(1, result.size(), "Should have one student's average");
    assertEquals(85.0, result.get("John Doe"), "Average should be 85.0");
  }
  
  /**
   * Tests calculating average grades when a student has no grades.
   * Verifies that the result is null for students without grades.
   */
  @Test
  void testGetAverageGradePerStudentWithNoGrades() {
    // Mock repository response with student having no grades
    when(studentRepository.findAll()).thenReturn(Arrays.asList(student2));
    
    // Test the service
    Map<String, Double> result = statisticsService.getAverageGradePerStudent();
    
    assertNotNull(result, "Result should not be null");
    assertEquals(1, result.size(), "Should have one student entry");
    assertNull(result.get("Jane Smith"), "Average should be null for student with no grades");
  }

  /**
   * Tests calculating average grades for a single module with multiple grades.
   * Verifies that the average is calculated correctly.
   */
  @Test
  void testGetAverageGradePerModule() {
    // Add grades to module1
    Grade grade1 = new Grade(75, module1);
    Grade grade2 = new Grade(85, module1);
    module1.setGrades(Arrays.asList(grade1, grade2));
    
    // Mock repository response
    when(moduleRepository.findAll()).thenReturn(Arrays.asList(module1));
    
    // Test the service
    Map<String, Double> result = statisticsService.getAverageGradePerModule();
    
    assertNotNull(result, "Result should not be null");
    assertEquals(1, result.size(), "Should have one module's average");
    assertEquals(80.0, result.get("COMP0010 - Software Engineering"), "Average should be 80.0");
  }

  /**
   * Tests calculating average grades when a module has no grades.
   * Verifies that the result is null for modules without grades.
   */
  @Test
  void testGetAverageGradePerModuleWithNoGrades() {
    // Mock repository response with module having no grades
    when(moduleRepository.findAll()).thenReturn(Arrays.asList(module2));
    
    // Test the service
    Map<String, Double> result = statisticsService.getAverageGradePerModule();
    
    assertNotNull(result, "Result should not be null");
    assertEquals(1, result.size(), "Should have one module entry");
    assertNull(result.get("COMP0011 - Database Systems"), "Average should be null for module with no grades");
  }
} 