package grader;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.List;

class QualityTest {

  private static final Path SRC = Path.of(System.getProperty("user.dir")).resolve("src/main/java");

  @Test
  void testControllerHasMappingAnnotations() throws IOException {
      List<Path> files = findFiles(SRC, ".java");
      boolean hasMappings = files.stream().anyMatch(f -> {
          try {
              String content = Files.readString(f);
              return content.contains("@GetMapping")
                  || content.contains("@PostMapping")
                  || content.contains("@RequestMapping");
          } catch (IOException e) { return false; }
      });
      assertTrue(hasMappings, "No mapping annotations found (@GetMapping, @PostMapping, @RequestMapping)");
  }

  @Test
  void testHasServiceLayer() throws IOException {
      List<Path> files = findFiles(SRC, ".java");
      boolean hasService = files.stream().anyMatch(f -> {
          try {
              return Files.readString(f).contains("@Service");
          } catch (IOException e) { return false; }
      });
      assertTrue(hasService, "No class with @Service annotation found — add a service layer");
  }

  @Test
  void testUsesConstructorInjection() throws IOException {
      List<Path> files = findFiles(SRC, ".java");
      assertFalse(files.isEmpty(), "No .java files found in src/main/java/");
      boolean usesAutowired = files.stream().anyMatch(f -> {
          try {
              return Files.readString(f).contains("@Autowired");
          } catch (IOException e) { return false; }
      });
      assertFalse(usesAutowired, "Avoid @Autowired on fields — use constructor injection instead");
  }

  @Test
  void testNoTodoComments() throws IOException {
      List<Path> files = findFiles(SRC, ".java");
      for (Path file : files) {
          String content = Files.readString(file);
          assertFalse(content.contains("// TODO"),
              file.getFileName() + " has TODO comments — complete your implementation");
      }
  }

  private List<Path> findFiles(Path dir, String extension) throws IOException {
      List<Path> result = new ArrayList<>();
      if (!Files.exists(dir)) return result;
      Files.walkFileTree(dir, new SimpleFileVisitor<>() {
          @Override
          public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
              if (file.toString().endsWith(extension)) result.add(file);
              return FileVisitResult.CONTINUE;
          }
      });
      return result;
  }
}
