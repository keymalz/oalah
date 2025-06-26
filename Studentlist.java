package TableView;


import javafx.collections.FXCollections;
import javafx.collections.ObservableList;

public class Studentlist {

    private ObservableList<Student> students;

    public Studentlist() {
        this.students = FXCollections.observableArrayList();
    }

    public ObservableList<Student> get() {
        return this.students;
    }

    public void add(Student student) {
        this.students.add(student);
    }

    public void setDummy() {
        this.students.add(new Student("111", "Agus"));
        this.students.add(new Student("222", "Budi"));
        this.students.add(new Student("333", "Caca"));
    }
}