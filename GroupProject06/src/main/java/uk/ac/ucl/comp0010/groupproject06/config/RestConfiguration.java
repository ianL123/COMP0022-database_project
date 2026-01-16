package uk.ac.ucl.comp0010.groupproject06.config;


import org.springframework.context.annotation.Configuration;
import org.springframework.data.rest.core.config.RepositoryRestConfiguration;
import org.springframework.data.rest.webmvc.config.RepositoryRestConfigurer;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import uk.ac.ucl.comp0010.groupproject06.model.Grade;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.model.Student;

/**
 * This class is used to configure the REST API to expose the IDs of the entities.
 */
@Configuration
public class RestConfiguration implements RepositoryRestConfigurer {

  @Override
  public void configureRepositoryRestConfiguration(RepositoryRestConfiguration config,
      CorsRegistry cors) {
    config.exposeIdsFor(Student.class);
    config.exposeIdsFor(Module.class);
    config.exposeIdsFor(Grade.class);
  }

}