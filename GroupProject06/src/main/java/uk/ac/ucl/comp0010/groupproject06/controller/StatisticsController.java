package uk.ac.ucl.comp0010.groupproject06.controller;

import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import uk.ac.ucl.comp0010.groupproject06.service.StatisticsService;

/**
 * Controller for handling the statistics page (extension).
 * Gives average score per students and modules.
 */
@RestController
@RequestMapping("/statistics")
public class StatisticsController {

  @Autowired
  private StatisticsService statisticsService;

  @GetMapping("/average/student")
  public Map<String, Double> getAverageGradePerStudent() {
    return statisticsService.getAverageGradePerStudent();
  }

  @GetMapping("/average/module")
  public Map<String, Double> getAverageGradePerModule() {
    return statisticsService.getAverageGradePerModule();
  }
}
