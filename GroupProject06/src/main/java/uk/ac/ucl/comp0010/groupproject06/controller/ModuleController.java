package uk.ac.ucl.comp0010.groupproject06.controller;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;

/**
 * Controller class for handling HTTP requests related to modules.
 */
@RestController
@RequestMapping("/api")
public class ModuleController {
  @Autowired
  private ModuleRepository moduleRepository;

  /**
   * Get all modules.
   *
   * @return A list of all modules.
   */
  @GetMapping("/modules")
  public ResponseEntity<List<Module>> getAllModules() {
    List<Module> modules = new ArrayList<>();
    moduleRepository.findAll().forEach(modules::add);

    return ResponseEntity.ok(modules);
  }

  /**
   * Get a module by its code.
   *
   * @param code The code of the module.
   * @return The module if found, otherwise a 404 response.
   */
  @PutMapping("/{code}")
  public ResponseEntity<Module> updateModule(
            @PathVariable String code, @RequestBody Module updatedModule
  ) {
    Optional<Module> existingModule = moduleRepository.findById(code);
    if (existingModule.isPresent()) {
      Module module = existingModule.get();
      module.setName(updatedModule.getName());
      module.setMnc(updatedModule.isMnc());
      moduleRepository.save(module);
      return ResponseEntity.ok(module);
    } else {
      return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
    }
  }
} 