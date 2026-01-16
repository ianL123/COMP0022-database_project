package uk.ac.ucl.comp0010.groupproject06.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;

/**
 * A class representing the registration of a student to a module.
 */
@Entity
public class Registration {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private int id;

  @ManyToOne
  private Module module;

  @ManyToOne
  private Student student;

  public Registration() {
  }
  /**
   * Constructs a registration.
   *
   * @param module the module for registration
   * @param student the student being registered to the module
   */

  public Registration(Module module, Student student) {
    this.module = module;
    this.student = student;
  }

  // Getters
  public Module getModule() {
    return module;
  }

  public Student getStudent() {
    return student;
  }

  // Setters
  public void setModule(Module module) {
    this.module = module;
  }

  public void setStudent(Student student) {
    this.student = student;
  }
}
