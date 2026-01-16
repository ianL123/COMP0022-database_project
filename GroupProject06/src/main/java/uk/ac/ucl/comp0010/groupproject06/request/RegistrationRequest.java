package uk.ac.ucl.comp0010.groupproject06.request;

/**
 * Represents a request to register a student to a module.
 */
public class RegistrationRequest {
  private Long studentId;
  private String moduleCode;

  public RegistrationRequest() {}

  public RegistrationRequest(Long studentId, String moduleCode) {
    this.studentId = studentId;
    this.moduleCode = moduleCode;
  }

  public Long getStudentId() {
    return studentId;
  }

  public void setStudentId(Long studentId) {
    this.studentId = studentId;
  }

  public String getModuleCode() {
    return moduleCode;
  }

  public void setModuleCode(String moduleCode) {
    this.moduleCode = moduleCode;
  }
}
