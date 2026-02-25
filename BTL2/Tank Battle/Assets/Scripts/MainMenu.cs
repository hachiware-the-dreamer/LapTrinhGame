using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenuController : MonoBehaviour
{
    public string gameSceneName = "SampleScene";

    public void PlayGame()
    {
        Debug.Log("Loading Game...");
        SceneManager.LoadScene(gameSceneName);
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