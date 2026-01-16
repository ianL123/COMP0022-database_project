package uk.ac.ucl.comp0010.groupproject06.exception;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.Test;

/**
 * Test class for the NoRegistrationException.
 * Tests the creation and behavior of the custom exception used for registration errors.
 */
public class NoRegistrationExceptionTest {
  
  /**
   * Tests the creation of a NoRegistrationException with a custom message.
   * Verifies that the exception is created correctly and contains the expected message.
   */
  @Test
  void testExceptionCreation() {
    String errorMessage = "Already registered for this module";
    NoRegistrationException exception = new NoRegistrationException(errorMessage);
    
    assertNotNull(exception, "Exception should not be null");
    assertEquals(errorMessage, exception.getMessage(), "Error message should match");
  }
  
  /**
   * Tests that NoRegistrationException properly inherits from Exception.
   * Verifies the inheritance hierarchy of the exception class.
   */
  @Test
  void testExceptionInheritance() {
    NoRegistrationException exception = new NoRegistrationException("Test message");
    
    assertNotNull(exception, "Exception should not be null");
    assertEquals(Exception.class, exception.getClass().getSuperclass(), 
      "NoRegistrationException should inherit from Exception");
  }
} 