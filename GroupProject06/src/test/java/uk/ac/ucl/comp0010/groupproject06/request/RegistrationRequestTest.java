package uk.ac.ucl.comp0010.groupproject06.request;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.Test;

/**
 * Test class for the RegistrationRequest model.
 * Tests the creation and manipulation of registration request objects.
 */
public class RegistrationRequestTest {
  
  /**
   * Tests the default constructor of RegistrationRequest.
   * Verifies that a new instance can be created without parameters.
   */
  @Test
  void testDefaultConstructor() {
    RegistrationRequest request = new RegistrationRequest();
    assertNotNull(request, "Request should not be null");
  }
  
  /**
   * Tests the parameterized constructor of RegistrationRequest.
   * Verifies that a new instance can be created with student ID and module code.
   */
  @Test
  void testParameterizedConstructor() {
    Long studentId = 1L;
    String moduleCode = "COMP0010";
    
    RegistrationRequest request = new RegistrationRequest(studentId, moduleCode);
    
    assertNotNull(request, "Request should not be null");
    assertEquals(studentId, request.getStudentId(), "Student ID should match");
    assertEquals(moduleCode, request.getModuleCode(), "Module code should match");
  }
  
  /**
   * Tests the setters and getters of RegistrationRequest.
   * Verifies that values can be set and retrieved correctly.
   */
  @Test
  void testSettersAndGetters() {
    RegistrationRequest request = new RegistrationRequest();
    
    Long studentId = 2L;
    String moduleCode = "COMP0011";
    
    request.setStudentId(studentId);
    request.setModuleCode(moduleCode);
    
    assertEquals(studentId, request.getStudentId(), "Student ID should match after setting");
    assertEquals(moduleCode, request.getModuleCode(), "Module code should match after setting");
  }
} 