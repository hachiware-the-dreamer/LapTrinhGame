using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenuController : MonoBehaviour
{
    public string mapSelectionSceneName = "MapSelectionScene";

    public void PlayGame()
    {
        Debug.Log("Loading Map Selection...");
        SceneManager.LoadScene(mapSelectionSceneName);
    }

    public void QuitGame()
    {
        Debug.Log("Quitting Game...");
        
        Application.Quit();
        
        #if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
        #endif
    }
}