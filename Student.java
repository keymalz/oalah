package TableView;
import javafx.beans.property.SimpleStringProperty;

public class Student {

    private final SimpleStringProperty name;
    private final SimpleStringProperty nim;

    public Student(String nim, String name) {
        this.nim = new SimpleStringProperty(nim);
        this.name = new SimpleStringProperty(name);
    }

    public String getNim() {
        return nim.get();
    }

    public String getName() {
        return name.get();
    }

    public void setNim(String nim) {
        this.nim.set(nim);
    }

    public void setName(String name) {
        this.name.set(name);
    }

    public SimpleStringProperty nimProperty() {
        return nim;
    }

    public SimpleStringProperty nameProperty() {
        return name;
    }
}