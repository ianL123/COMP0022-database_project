package uk.ac.ucl.comp0010.groupproject06.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import uk.ac.ucl.comp0010.groupproject06.exception.NoGradeAvailableException;
import uk.ac.ucl.comp0010.groupproject06.exception.NoRegistrationException;

/**
 * The students in the university.
 * By creating a student, the student will have a unique ID, first name,
 * last name, username and email.
 * A student can have grades and registrations with modules.
 */
@Entity
public class Student {

  @Id
  private Long id;

  private String firstName;
  private String lastName;
  private String username;
  private String email;

  @OneToMany(mappedBy = "student")
  private List<Grade> grades = new ArrayList<>();

  @OneToMany(mappedBy = "student", cascade = CascadeType.ALL)
  @JsonIgnore
  private List<Registration> registrations = new ArrayList<>();

  public Student() {
  }

  /**
   * Constructs a Student.
   *
   * @param id the ID of the student
   * @param firstName the first name of the student
   * @param lastName the last name of the student
   * @param username the username of the student
   * @param email the email of the student
   */
  public Student(Long id, String firstName, String lastName, String username, String email) {
    this.id = id;
    this.firstName = firstName;
    this.lastName = lastName;
    this.username = username;
    this.email = email;
  }

  /**
   * Computes the average grade of the student base on all the scores he has.
   *
   * @return the average grade of the student
   * @throws NoGradeAvailableException if there are no grades available
   */
  public Float computeAverage() throws NoGradeAvailableException {
    if (grades.isEmpty()) {
      throw new NoGradeAvailableException("No grades available for student ID: " + id);
    }
    int totalScore = grades.stream().mapToInt(Grade::getScore).sum();
    return (float) totalScore / grades.size();
  }

  /**
   * Adds a grade to the student's grade list.
   *
   * @param grade the grade to be added
   */
  public void addGrade(Grade grade) {
    grades.add(grade);
  }

  /**
   * Retrieves the grade for a specific module.
   *
   * @param module the module for which to retrieve the grade
   * @return the grade for the specified module
   * @throws NoGradeAvailableException if no grade is available for the module
   */
  public Grade getGrade(Module module) throws NoGradeAvailableException {
    Optional<Grade> grade = grades.stream()
            .filter(g -> g.getModule().equals(module))
            .findFirst();
    return grade.orElseThrow(() -> new NoGradeAvailableException(
            "No grade available for module: " + module.getCode() + " for student ID: " + id));
  }

  /**
 * Adds a registration.
 *
 * @param registration the registration to be added
 * @throws NoRegistrationException if the student is already registered for the module
 */
  public void registerModule(Registration registration) throws NoRegistrationException {
    if (!registrations.contains(registration)) {
      registrations.add(registration);
    } else {
      throw new NoRegistrationException("Already registered for this module");
    }
  }

  // Getters
  public Long getId() {
    return id;
  }

  public String getFirstName() {
    return firstName;
  }

  public String getLastName() {
    return lastName;
  }

  public String getUsername() {
    return username;
  }

  public String getEmail() {
    return email;
  }

  public List<Grade> getGrades() {
    return new ArrayList<>(grades); // Defensive copy to prevent modification of original list
  }

  public List<Registration> getRegistrations() {
    return new ArrayList<>(registrations);
  }

  // Setters
  public void setId(Long id) {
    this.id = id;
  }

  public void setFirstName(String firstName) {
    this.firstName = firstName;
  }

  public void setLastName(String lastName) {
    this.lastName = lastName;
  }

  public void setUsername(String username) {
    this.username = username;
  }

  public void setEmail(String email) {
    this.email = email;
  }

}
