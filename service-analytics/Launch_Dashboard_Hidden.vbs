Set WshShell = CreateObject("WScript.Shell")
CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
Set FSO = CreateObject("Scripting.FileSystemObject")

' Change to the app directory
WshShell.CurrentDirectory = CurrentDirectory

' Determine Python command to use
PythonCmd = "python"

' Try 'py' first, and if successful, use it
On Error Resume Next
TestResult = WshShell.Run("py --version", 0, True)
If Err.Number = 0 And TestResult = 0 Then
    PythonCmd = "py"
Else
    ' Try 'python' as fallback
    TestResult = WshShell.Run("python --version", 0, True)
    If Err.Number <> 0 Or TestResult <> 0 Then
        ' Neither works - show error and exit
        WshShell.Popup "Python was not found. Please install Python or run Setup.bat first.", 0, "Error", 16
        WScript.Quit
    End If
End If
On Error Goto 0

' Determine which virtual environment to use
VenvPath = ""
If FSO.FolderExists(CurrentDirectory & "\.venv") Then
    VenvPath = ".venv\Scripts\activate.bat"
ElseIf FSO.FolderExists(CurrentDirectory & "\venv") Then
    VenvPath = "venv\Scripts\activate.bat"
ElseIf FSO.FolderExists(CurrentDirectory & "\env") Then
    VenvPath = "env\Scripts\activate.bat"
End If

' Open browser first
WshShell.Run "cmd /c start http://localhost:8503", 0, True

' Run Streamlit in hidden mode
If VenvPath <> "" Then
    ' Run with virtual environment
    WshShell.Run "cmd /c " & VenvPath & " && " & PythonCmd & " -m streamlit run app.py", 0, False
Else
    ' Try with system Python
    WshShell.Run "cmd /c " & PythonCmd & " -m streamlit run app.py", 0, False
End If

' Display a notification
WshShell.Popup "Service Analytics Dashboard is starting... " & vbCrLf & vbCrLf & "The dashboard will open in your browser at http://localhost:8503", 5, "Dashboard Started", 64 