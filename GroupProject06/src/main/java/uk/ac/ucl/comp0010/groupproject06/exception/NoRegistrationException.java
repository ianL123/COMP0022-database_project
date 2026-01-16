package uk.ac.ucl.comp0010.groupproject06.exception;

/**
 * Custom exception thrown when no registration is available for a given student.
 * Okay to be thrown for whatever registration problem.
 */
public class NoRegistrationException extends Exception {
  public NoRegistrationException(String message) {
    super(message);
  }  
}
