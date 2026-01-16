package uk.ac.ucl.comp0010.groupproject06.exception;

/**
 * Custom exception thrown when no grade is available for a given module.
 * Okay to be thrown for whatever grade problem.
 */
public class NoGradeAvailableException extends Exception {
  public NoGradeAvailableException(String message) {
    super(message);
  }
}
