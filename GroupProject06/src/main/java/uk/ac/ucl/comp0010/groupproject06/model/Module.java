package uk.ac.ucl.comp0010.groupproject06.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import java.util.ArrayList;
import java.util.List;
import uk.ac.ucl.comp0010.groupproject06.exception.NoGradeAvailableException;

/**
 * Module is the section of study that student can take.
 * The module code is unique and is used to identify the module.
 * The module name is the name of the module.
 * A module can set to be mnc or not.
 * Foreach student choose a module, a registration will be created.
 * Grades can be added between a student and a module.
 */
@Entity
public class Module {

  @Id
  @Column(nullable = false, unique = true)
  private String code;

  @Column(nullable = false)
  private String name;

  @Column(nullable = false)
  private boolean mnc;

  @OneToMany(mappedBy = "module")
  @JsonIgnore
  private List<Grade> grades = new ArrayList<>();


  public Module() {
  }
  /**
   * Constructs a module.
   *
   * @param code the unique code of the module
   * @param name the name of the module
   * @param mnc indicates if the module is mandatory and non-condonable
   */

  public Module(String code, String name, boolean mnc) {
    this.code = code;
    this.name = name;
    this.mnc = mnc;
  }

  // Getters
  public String getId() {
    return code;
  }

  public String getCode() {
    return code;
  }

  public String getName() {
    return name;
  }

  public boolean isMnc() {
    return mnc;
  }

  // Setters
  public void setCode(String code) {
    this.code = code;
  }

  public void setName(String name) {
    this.name = name;
  }

  public void setMnc(boolean mnc) {
    this.mnc = mnc;
  }

  /**
   * Computes the average grade for this module.
   *
   * @return the average grade for the module
   * @throws NoGradeAvailableException if no grades are available for this module
   */
  public Float computeAverageGrade() throws NoGradeAvailableException {
    if (grades.isEmpty()) {
      throw new NoGradeAvailableException("No grades available for module: " + code);
    }
    int totalScore = grades.stream().mapToInt(Grade::getScore).sum();
    return (float) totalScore / grades.size();
  }

  public List<Grade> getGrades() {
    return new ArrayList<>(grades);
  }

  public void setGrades(List<Grade> grades) {
    this.grades = grades;
  }
}
