package uk.ac.ucl.comp0010.groupproject06.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Controller class for handling HTTP requests related to grades.
 * As grade is a relation between student and module.
 * The CRUD operations are in the student controller.
 * We leave this controller considering the further development.
 */
@RestController
@RequestMapping("/grades")
public class GradesController {

}
