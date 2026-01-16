package uk.ac.ucl.comp0010.groupproject06.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;

/**
 * A class representing a grade aggregated with a module.
 * Grade contain a Integer to show the score of a student on a module.
 */
@Entity
public class Grade {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private int id;

  @Column(nullable = false)
  private Integer score;

  @ManyToOne
  private Module module;

  @ManyToOne
  @JsonIgnore
  private Student student;

  public Grade() {
  }
  /**
   * Constructs a grade.
   *
   * @param score the score of the grade
   * @param module the module that the grade belongs to
   */

  public Grade(Integer score, Module module) {
    this.score = score;
    this.module = module;
  }

  // Getters
  public int getId() {
    return id;
  }

  public Integer getScore() {
    return score;
  }

  public Module getModule() {
    return module;
  }

  public Student getStudent() {
    return student;
  }

  // Setters
  public void setScore(Integer score) {
    this.score = score;
  }

  public void setModule(Module module) {
    this.module = module;
  }

  public void setStudent(Student student) {
    this.student = student;
  }
}
